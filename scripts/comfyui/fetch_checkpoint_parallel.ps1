# FACTORIA / ComfyUI - restartable parallel download of large model files.
#
# Why: huggingface.co throttles a single TCP stream on this host to ~20-60 KB/s; 12 parallel
# range requests reach ~0.9-1.0 MB/s. Because a 7 GB file then takes hours, the transfer must
# survive restarts: every byte range is downloaded into "<target>.parts\part_<i>.bin" and the
# parts directory is REUSED on the next run, so a re-run never re-downloads finished ranges.
#
# Ranges are deterministic: they are computed over the WHOLE file with a fixed chunk size
# (ceil(total/Connections)), independent of what is already on disk. Only when every part is
# complete is the target assembled (write to <target>.new, then replace) and verified by SHA-256.
#
# Usage:
#   powershell -ExecutionPolicy Bypass -File fetch_checkpoint_parallel.ps1 `
#       -Url <url> -Target <file> -ExpectedSha256 <hex> -TotalBytes <n> [-Connections 12]
param(
    [Parameter(Mandatory = $true)][string]$Url,
    [Parameter(Mandatory = $true)][string]$Target,
    [Parameter(Mandatory = $true)][string]$ExpectedSha256,
    [Parameter(Mandatory = $true)][int64]$TotalBytes,
    [int]$Connections = 12,
    [int]$MaxRounds = 40,
    [int]$MaxSeconds = 0
)

$ErrorActionPreference = 'Stop'
$targetDir = Split-Path $Target -Parent
New-Item -ItemType Directory -Force -Path $targetDir | Out-Null
$partsDir = "$Target.parts"
New-Item -ItemType Directory -Force -Path $partsDir | Out-Null

# already finished?
if ((Test-Path $Target) -and (Get-Item $Target).Length -eq $TotalBytes) {
    $sha = (Get-FileHash -Path $Target -Algorithm SHA256).Hash.ToLower()
    if ($sha -eq $ExpectedSha256.ToLower()) {
        "already_complete=true sha256=$sha"
        "SHA256_OK"
        exit 0
    }
    "existing_target_sha_mismatch -> rebuilding from parts"
}

$chunk = [int64][math]::Ceiling($TotalBytes / $Connections)
"target=$Target"
"total_bytes=$TotalBytes connections=$Connections chunk_bytes=$chunk parts_dir=$partsDir"

$parts = @()
for ($i = 0; $i -lt $Connections; $i++) {
    $start = $i * $chunk
    if ($start -ge $TotalBytes) { break }
    $end = [math]::Min($start + $chunk - 1, $TotalBytes - 1)
    $parts += [pscustomobject]@{
        Index = $i; Start = $start; End = $end
        Size  = $end - $start + 1
        Path  = (Join-Path $partsDir "part_$i.bin")
    }
}

$sw = [Diagnostics.Stopwatch]::StartNew()

# Recover from an interrupted run: tails left by the previous round are appended to
# their parts before any new request, so no downloaded byte is ever thrown away.
foreach ($p in $parts) {
    $tail = "$($p.Path).tail"
    if ((Test-Path $tail) -and ((Get-Item $tail).Length -gt 0)) {
        $have = if (Test-Path $p.Path) { (Get-Item $p.Path).Length } else { 0 }
        if ($have + (Get-Item $tail).Length -le $p.Size) {
            $fsA = [System.IO.File]::Open($p.Path, [System.IO.FileMode]::Append, [System.IO.FileAccess]::Write)
            try {
                $bytes = [System.IO.File]::ReadAllBytes($tail)
                $fsA.Write($bytes, 0, $bytes.Length)
            } finally { $fsA.Dispose() }
            "recovered_tail part=$($p.Index) bytes=$((Get-Item $tail).Length)"
        }
        Remove-Item $tail -Force
    }
}

for ($round = 1; $round -le $MaxRounds; $round++) {
    $pending = @($parts | Where-Object {
            -not ((Test-Path $_.Path) -and ((Get-Item $_.Path).Length -eq $_.Size))
        })
    if ($pending.Count -eq 0) { "round=$round ALL_PARTS_COMPLETE"; break }
    if ($MaxSeconds -gt 0 -and $sw.Elapsed.TotalSeconds -gt $MaxSeconds) { "TIME_LIMIT_REACHED"; exit 7 }
    "round=$round pending_parts=$($pending.Count)/$($parts.Count) elapsed_s=$([math]::Round($sw.Elapsed.TotalSeconds,0))"
    $procs = @()
    foreach ($p in $pending) {
        # Byte-level resume inside a part: keep the already downloaded prefix and fetch
        # only the missing tail into <part>.tail (curl cannot append to an existing file).
        $have = 0
        if (Test-Path $p.Path) { $have = (Get-Item $p.Path).Length }
        if ($have -gt $p.Size) { Remove-Item $p.Path -Force; $have = 0 }
        $tail = "$($p.Path).tail"
        if (Test-Path $tail) { Remove-Item $tail -Force }
        if ($have -eq $p.Size) { continue }
        $rangeStart = $p.Start + $have
        $out = if ($have -gt 0) { $tail } else { $p.Path }
        $procs += Start-Process -FilePath 'curl.exe' -PassThru -WindowStyle Hidden -ArgumentList @(
            '-L', '--fail', '--silent', '--show-error',
            '--speed-limit', '1024', '--speed-time', '60', '--max-time', '3600',
            '-r', "$rangeStart-$($p.End)", '-o', $out, $Url)
    }
    foreach ($pr in $procs) { $pr.WaitForExit() }
    # merge tails into their parts, then report how many parts are complete
    foreach ($p in $pending) {
        $tail = "$($p.Path).tail"
        if ((Test-Path $tail) -and ((Get-Item $tail).Length -gt 0)) {
            $fsA = [System.IO.File]::Open($p.Path, [System.IO.FileMode]::Append, [System.IO.FileAccess]::Write)
            try {
                $bytes = [System.IO.File]::ReadAllBytes($tail)
                $fsA.Write($bytes, 0, $bytes.Length)
            } finally { $fsA.Dispose() }
            Remove-Item $tail -Force
        }
    }
    $done = @($parts | Where-Object { (Test-Path $_.Path) -and ((Get-Item $_.Path).Length -eq $_.Size) }).Count
    "round=$round complete_parts=$done/$($parts.Count) elapsed_s=$([math]::Round($sw.Elapsed.TotalSeconds,0))"
}

$missing = @($parts | Where-Object { -not ((Test-Path $_.Path) -and ((Get-Item $_.Path).Length -eq $_.Size)) })
if ($missing.Count -gt 0) {
    "INCOMPLETE parts=$($missing.Count) - run the same command again to continue"
    exit 7
}

$tmp = "$Target.new"
if (Test-Path $tmp) { Remove-Item $tmp -Force }
$fs = [System.IO.File]::Open($tmp, [System.IO.FileMode]::Create, [System.IO.FileAccess]::Write)
try {
    foreach ($p in $parts) {
        $bytes = [System.IO.File]::ReadAllBytes($p.Path)
        $fs.Write($bytes, 0, $bytes.Length)
    }
} finally { $fs.Dispose() }

if ((Get-Item $tmp).Length -ne $TotalBytes) {
    "ASSEMBLED_SIZE_MISMATCH got=$((Get-Item $tmp).Length) expected=$TotalBytes"
    exit 3
}
Move-Item -Path $tmp -Destination $Target -Force
Remove-Item $partsDir -Recurse -Force -ErrorAction SilentlyContinue

$sha = (Get-FileHash -Path $Target -Algorithm SHA256).Hash.ToLower()
"sha256=$sha"
if ($sha -ne $ExpectedSha256.ToLower()) { "SHA256_MISMATCH expected=$($ExpectedSha256.ToLower())"; exit 4 }
"SHA256_OK"
exit 0
