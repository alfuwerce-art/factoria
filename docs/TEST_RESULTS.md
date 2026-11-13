# TEST_RESULTS — CubeGame Factory Lab

Журнал фактических испытаний. Формат записи соответствует ТЗ §7.
Правило: `NOT_TESTED` / `PARTIAL` / `BLOCKED` ставятся честно; `SMOKE_PASS` — только после реального запуска.

---

## PREP-00 — аудит ПК и установленного ПО

```yaml
id: PREP-00
status: READY_FOR_REVIEW
machine: WINDOWS_11
kind: audit
software: OS / CPU / RAM / GPU / disks / installed tooling
version: Windows 11 Pro 10.0.26200; Ryzen 5 7535HS; 32 GB DDR5-5600; RTX 4060 Laptop 8188 MiB
source_url: n/a (локальный аудит)
license: n/a
install_location: n/a
sample_asset: n/a
command: |
  logs/PREP-00_detection_2026-11-13.txt — консолидированный запуск:
  Get-CimInstance Win32_OperatingSystem | Win32_ComputerSystem | Win32_Processor | Win32_PhysicalMemory
  nvidia-smi --query-gpu=name,driver_version,memory.total,memory.used,memory.free,temperature.gpu,utilization.gpu --format=csv
  Get-Volume | Get-ItemProperty HKLM/HKCU ...\Uninstall\* 
  Get-Command python,py,pip,git,node,npm,code,blender,ffmpeg,ollama,n8n,7z,dotnet
  py -0p ; python -m pip --version ; git --version ; git config --get user.name
  Get-ChildItem C:\,D:\ -Recurse -Depth 3..4 -Filter blender.exe / Cascadeur*.exe / *omfy*
  Get-NetTCPConnection -LocalPort 8188 / 11434
input: локальная машина
output: D:\Projects\CubeGame Factory\logs\PREP-00_detection_2026-11-13.txt (177 строк, UTF-8)
checks:
  - name: Windows / CPU / RAM определены
    result: PASS
  - name: VRAM определена инструментально (nvidia-smi)
    result: PASS
  - name: Свободное место на дисках определено
    result: PASS
  - name: Python / Git / VS Code / Unity / Ollama обнаружены с версиями и путями
    result: PASS
  - name: Blender обнаружен
    result: NOT_FOUND
  - name: ComfyUI обнаружен
    result: NOT_FOUND
  - name: Cascadeur обнаружен
    result: NOT_FOUND
  - name: n8n / Node.js обнаружены
    result: NOT_FOUND
  - name: Unity запускался
    result: NOT_TESTED (запрещено на этом этапе)
issues:
  - ComfyUI отсутствует, хотя ТЗ/память указывают его как имеющийся (USER_REPORTED) — нужен путь от пользователя
  - Blender отсутствует — блокирует PREP-01
  - Git user.name/user.email не настроены
  - C: свободно 68.2 ГБ — мало для весов
  - python3 в PATH — заглушка Microsoft Store
  - реестровая запись 7-Zip ведёт в несуществующий каталог
next_action: PREP-01 — установить Blender 5.2.4 LTS (официальный zip) на D:, проверить GUI и background, затем Rigify
```

### Ключевые измеренные значения (2026-11-13 11:43 MSK)

| Метрика | Значение |
|---|---|
| VRAM всего / занято / свободно | 8188 MiB / 1251 MiB / **6706 MiB** |
| Температура GPU / загрузка | 57 °C / 53 % (фон: браузеры, wallpaper engine, NVIDIA Overlay) |
| RAM всего / свободно | 31.24 ГБ / **18.67 ГБ** |
| Диск C: / D: свободно | 68.2 ГБ / **642.1 ГБ** |
| CUDA | драйвер 610.47, UMD 13.3, Toolkit (`nvcc`) отсутствует |

### Обнаружено с версиями

| Инструмент | Версия | Путь |
|---|---|---|
| Python | 3.13.14 | `C:\Users\bow\AppData\Local\Programs\Python\Python313\python.exe` |
| Python (alt) | 3.14.6 | `C:\Users\bow\AppData\Local\Python\pythoncore-3.14-64\python.exe` |
| pip | 26.1.2 | `...\Python313\Scripts\pip.exe` |
| Git | 2.55.0.windows.1 | `C:\Program Files\Git\cmd\git.exe` |
| VS Code | 1.145.2 | `C:\Users\bow\AppData\Local\Programs\Microsoft VS Code\bin\code.cmd` |
| Unity Hub | 3.22.5 | `D:\Unity Hub\Unity Hub.exe` |
| Unity Editor | 6000.3.27f2 | `D:\Unity\Hub\Editor\6000.3.27f2\Editor\Unity.exe` |
| Unity Editor | 6000.6.7f1 | `D:\Unity\6000.6.7f1\Editor\Unity.exe` |
| Ollama | 0.40.10 (не запущен) | `C:\Users\bow\AppData\Local\Programs\Ollama\ollama.exe` |
| .NET | 7.0.14 / 8.0.34 | `C:\Program Files\dotnet` |
| WinRAR | 7.13 | `C:\Program Files\WinRAR` |

### Не обнаружено (подтверждено поиском)

Blender · Rigify (зависит от Blender) · ComfyUI · Cascadeur · n8n · Node.js/npm/pnpm (системный) · ffmpeg (в PATH) · 7-Zip (запись в реестре устарела) · CUDA Toolkit.

---

## PREP-01 — Blender / Rigify

```yaml
id: PREP-01
status: PLANNED
machine: WINDOWS_11
software: Blender
version: 5.2.4 LTS (цель; официальный индекс подтверждает сборку)
source_url: https://download.blender.org/release/Blender5.2/
license: GPL-2.0-or-later
install_location: TO_DISCOVER (план: D:\programs\Blender\5.2\)
sample_asset: собственный тестовый меш (будет создан в samples/original_test_assets)
command: NOT_RUN
input: n/a
output: n/a
checks:
  - name: GUI открывается
    result: NOT_TESTED
  - name: Headless (--background) запускается
    result: NOT_TESTED
  - name: Rigify add-on доступен
    result: NOT_TESTED
  - name: Metarig → generate rig на собственной фигуре
    result: NOT_TESTED
  - name: Automatic Weights (встроенный skinning)
    result: NOT_TESTED
issues: []
next_action: скачать blender-5.2.4-windows-x64.zip (405 779 142 байт) + .sha256, распаковать на D:, зафиксировать SHA-256
```

**Официальные данные загрузки (проверено 2026-11-13):**

| Файл | Размер (байт) | Источник |
|---|---|---|
| `blender-5.2.4-windows-x64.zip` | 405 779 142 | `https://ftp.blender.org/release/Blender5.2/` |
| `blender-5.2.4.sha256` | 777 | там же |

---

## PREP-02 — форматы и экспорт

```yaml
id: PREP-02
status: PLANNED
checks: []   # выполняется после PREP-01
```
