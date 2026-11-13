# FACTORIA / ComfyUI - resilient parallel download of large model files.
#
# Why: huggingface.co throttles a single TCP connection on this host to ~60-100 KB/s,
# while 4+ parallel range requests reach ~200 KB/s and more. The file is fetched as
# independent byte ranges, each range retried, then appended to the target in order and
# finally verified by SHA-256 - so a slow or broken connection cannot silently corrupt it.
#
# Usage:
#   powershell -ExecutionPolicy Bypass -File scripts\comfyui\fetch_checkpoint_parallel.ps1 `
#       -Url <hf resolve url> -Target <file> -ExpectedSha256 <hex> [-Connections 12] [-Resume]
param(
    [Parameter(Mandatory = $true)][string]$Url,
    [Parameter(Mandatory = $true)][string]$Target,
    [Parameter(Mandatory = $true)][string]$ExpectedSha256,
    [int]$Connections = 12,
    [int]$TotalBytes = 0,
    [switch]$Resume,
    [int]$MaxAttempts = 4
)

$ErrorActionPreference = 'Stop'
$targetDir = Split-Path $Target -Parent
New-Item -ItemType Directory -Force -Path $targetDir | Out-Null

if ($TotalBytes -le 0) {
    $head = & curl.exe -sIL $Url 2>$null
    $len = ($head | Select-String -Pattern '^content-length:\s*(\d+)' | Select-Object -Last 1)
    if (-not $len) { throw "cannot determine content-length for $Url" }
    $TotalBytes = [int64]$len.Matches[0].Groups[1].Value
}
"total_bytes=$TotalBytes connections=$Connections target=$Target"

$have = 0
if ($Resume -and (Test-Path $Target)) { $have = (Get-Item $Target).Length }
"existing_bytes=$have"

if ($have -eq $TotalBytes) {
    "already_complete=true"
} else {
    $remaining = $TotalBytes - $have
    $chunk = [int64][math]::Ceiling($remaining / $Connections)
    $tmp = Join-Path $targetDir ('.parts_' + [guid]::NewGuid().ToString('N').Substring(0, 8))
    New-Item -ItemType Directory -Force -Path $tmp | Out-Null
    $parts = @()
    for ($i = 0; $i -lt $Connections; $i++) {
        $start = $have + $i * $chunk
        if ($start -ge $TotalBytes) { break }
        $end = [math]::Min($start + $chunk - 1, $TotalBytes - 1)
        $parts += [pscustomobject]@{ Index = $i; Start = $start; End = $end; Path = (Join-Path $tmp "part_$i.bin") }
    }
    "parts=$($parts.Count) chunk_bytes=$chunk"

    $sw = [Diagnostics.Stopwatch]::StartNew()
    $pending = @($parts)
    $round = 0
    while ($pending.Count -gt 0) {
        $round++
        if ($round -gt $MaxAttempts) { throw "part download failed after $MaxAttempts rounds" }
        # launch every outstanding range concurrently - this is where the speed comes from
        $procs = @()
        foreach ($p in $pending) {
            $expected = $p.End - $p.Start + 1
            if ((Test-Path $p.Path) -and (Get-Item $p.Path).Length -eq $expected) { continue }
            $procs += Start-Process -FilePath 'curl.exe' -PassThru -WindowStyle Hidden -ArgumentList @(
                '-L', '--fail', '--silent', '--show-error',
                '--speed-limit', '2048', '--speed-time', '60', '--max-time', '1800',
                '-r', "$($p.Start)-$($p.End)", '-o', $p.Path, $Url)
        }
        if ($procs.Count -eq 0) { break }
        foreach ($pr in $procs) { $pr.WaitForExit() }
        $pending = @($pending | Where-Object {
                $exp = $_.End - $_.Start + 1
                -not ((Test-Path $_.Path) -and (Get-Item $_.Path).Length -eq $exp)
            })
        $done = $parts.Count - $pending.Count
        "round=$round done_parts=$done/$($parts.Count) elapsed_s=$([math]::Round($sw.Elapsed.TotalSeconds,0))"
        if ($pending.Count -gt 0) { Start-Sleep -Seconds 2 }
    }

    # append in order into the target file
    $fs = [System.IO.File]::Open($Target, [System.IO.FileMode]::Append, [System.IO.FileAccess]::Write)
    try {
        foreach ($p in $parts) {
            $bytes = [System.IO.File]::ReadAllBytes($p.Path)
            $fs.Write($bytes, 0, $bytes.Length)
            $fs.Flush()
            Remove-Item $p.Path -Force
        }
    } finally { $fs.Dispose() }
    Remove-Item $tmp -Recurse -Force -ErrorAction SilentlyContinue
    "download_elapsed_s=$([math]::Round($sw.Elapsed.TotalSeconds,0))"
}

$final = (Get-Item $Target).Length
"final_bytes=$final expected_bytes=$TotalBytes"
if ($final -ne $TotalBytes) { "SIZE_MISMATCH"; exit 3 }

$swHash = [Diagnostics.Stopwatch]::StartNew()
$sha = (Get-FileHash -Path $Target -Algorithm SHA256).Hash.ToLower()
"sha256=$sha"
"hash_seconds=$([math]::Round($swHash.Elapsed.TotalSeconds,1))"
if ($sha -ne $ExpectedSha256.ToLower()) { "SHA256_MISMATCH expected=$($ExpectedSha256.ToLower())"; exit 4 }
"SHA256_OK"
exit 0
