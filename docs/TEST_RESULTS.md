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

## PREP-01 — Blender / Rigify / skinning / экспорт

```yaml
id: PREP-01
status: READY_FOR_REVIEW          # каждая проверенная операция = SMOKE_PASS; приёмка за пользователем
machine: WINDOWS_11
software: Blender 5.2.4 LTS + штатный Rigify 0.6.10 + io_scene_fbx 5.15.0
version: 5.2.4 LTS (build hash cd5dc428cce1, build date 2026-11-10), Python внутри 3.13.13
source_url: https://download.blender.org/release/Blender5.2/blender-5.2.4-windows-x64.zip
license: GPL-2.0-or-later (файлы license\ в поставке; SHA-файл сборки опубликован)
install_location: D:\programs\Blender\5.2\blender.exe
download_sha256: bbd78f8931dc940444da4ff2983374930f9f5c092ae0e330588e9760bb9d967c
sha256_verified: YES (совпало с blender-5.2.4.sha256, строка windows-x64.zip)
install_size: 901.3 MB, 6530 файлов; PATH не изменялся
sample_asset: собственный процедурный манекен CG_PREP01_Mannequin (160 боксов по deform-костям + voxel remesh)
command: |
  $env:BLENDER_USER_CONFIG="D:\Projects\CubeGame Factory\environments\blender\config"
  & 'D:\programs\Blender\5.2\blender.exe' --background --factory-startup --python-exit-code 1 `
      --python "D:\Projects\CubeGame Factory\scripts\blender\prep01_rigify_skinning.py"
input: scripts\blender\prep01_rigify_skinning.py (создаёт геометрию сам, внешних ассетов нет)
output: |
  outputs\blender\prep01_rigify_skinned.blend      (574 КБ, риг+меш+позы)
  outputs\blender\prep01_rigify_skinned.fbx        (1.54 МБ, экспорт)
  outputs\blender\prep01_rest_pose.png             (evidence, rest)
  outputs\blender\prep01_control_pose.png          (evidence, control-поза)
  outputs\blender\prep01_gui_open.png              (скриншот GUI с открытым .blend)
  outputs\reports\prep01_rigify_skinning.json      (машиночитаемый отчёт)
checks:
  - name: GUI открывается и открывает лабораторный .blend
    result: PASS  (заголовок окна "prep01_rigify_skinned [D:\...\prep01_rigify_skinned.blend] - Blender 5.2.4 LTS", скриншот)
  - name: Headless (--background) запускается и сохраняет .blend
    result: PASS  (exit 0, prep01_bg_smoke.blend 86 КБ)
  - name: Rigify add-on доступен через API
    result: PASS  (bpy.ops.preferences.addon_enable(module='rigify') → enabled)
  - name: Metarig → generate rig на собственной фигуре
    result: PASS  (metarig 159 костей → rig 706 костей: 160 DEF + 546 control)
  - name: Parent with Automatic Weights (встроенный skinning)
    result: PASS  (160 vertex groups, 0 вершин без весов, Armature Modifier → rig)
  - name: Контрольные позы деформируют меш
    result: PASS  (IK-таргеты: 0.562 м, FK-режим: 0.332 м смещения вершин из depsgraph)
  - name: Экспорт FBX и обратный импорт
    result: PASS  (FBX 1.54 МБ → импорт: 1 armature, 1 mesh, 145 vgroups, поворот кости даёт 0.566 м)
issues:
  - addon_utils.enable('rigify') оставляет аддон полу-зарегистрированным: generate падает "'RigifyParameters' object has no attribute 'make_custom_pivot'"
  - 160 отдельных закрытых боксов ломают Bone Heat Weighting полностью (0 весов из 1280 вершин)
  - авто-веса не нормированы: сумма весов на вершину min 0.732 / p50 0.971 / max 0.9999
  - DEF-кости Rigify управляются constraints: прямой поворот DEF-кости не деформирует меш (0.0 м)
  - FBX экспортирует весь control rig (706 костей), а не чистый game-skeleton
next_action: PREP-02 — round-trip .blend/.fbx/.glb с контролем осей, масштаба, материалов и анимационного action
```

**Воспроизводимость:** полный прогон — 11.8–12.0 с (два прогона), пиковый рабочий набор процесса Blender 394–402 МБ,
свободная RAM до/после 20.43 → 20.45 ГБ, рендер Cycles на CPU (VRAM не занималась).
Лог: `logs\PREP-01_rigify_skinning_2026-11-13.txt`, диагностика: `logs\PREP-01_diagnostics_2026-11-13.txt`.

**Измеренные величины**

| Метрика | Значение |
|---|---|
| Костей в metarig / в сгенерированном rig | 159 / 706 |
| Deform-костей / control-костей | 160 / 546 |
| Вершин манекена: до / после voxel remesh | 1280 (160 оболочек) / 3926 (1 оболочка) |
| Vertex groups / вершин без весов | 160 / 0 |
| Сумма весов на вершину (min / p50 / max) | 0.7323 / 0.9711 / 0.9999 |
| Смещение меша: IK-контролы / FK-контролы / прямой DEF | 0.562 м / 0.332 м / 0.0 м |
| Рендер 640×800, Cycles CPU, 24 сэмпла | rest 1.0–1.3 с, posed 0.7 с |
| .blend / .fbx / отчёт | 587 722 Б / 1 577 084 Б / 5.9 КБ |
| FBX обратный импорт | 1 armature (706 костей), 1 mesh, 145 vgroups, 0.566 м |

**Найденные ловушки (проверено на практике, не теория)**

1. **`addon_utils.enable("rigify")` непригоден в 5.2.4.** Операторы регистрируются, но
   генерация падает: `Generation has thrown an exception: 'RigifyParameters' object has no
   attribute 'make_custom_pivot'`. Рабочий путь — `bpy.ops.preferences.addon_enable(module='rigify')`.
2. **Bone Heat Weighting не работает на несвязной геометрии.** 160 отдельных боксов
   (по одному на кость) → предупреждение `Bone Heat Weighting: failed to find solution for one
   or more bones` и **0 весов на всех 1280 вершинах**. После склейки боксов штатным
   Voxel Remesh в одну оболочку веса назначаются всем вершинам.
3. **Rigify управляет деформацией через control-кости.** Прямой поворот `DEF-upper_arm.L`
   не даёт смещения (0.0 м); работают `hand_ik.*` / `foot_ik.*` (IK) либо `*_fk.*` при
   `IK_FK = 1.0` на `upper_arm_parent.*` / `thigh_parent.*`.
4. **Авто-веса не нормированы:** 2426 из 3926 вершин имеют сумму весов ниже 1.0 на 2 %+.
   Для продакшена потребуется шаг нормализации (зафиксировано в `PIPELINE_GAPS.md`, F8).
5. **FBX несёт весь control rig (706 костей).** Для Unity нужен отдельный deform-only
   экспорт — это задача PREP-02/PREP-04, а не «уже готовый game skeleton».
6. **`rig_ui.py` и автозапуск скриптов:** при открытии .blend в GUI Blender показывает
   диалог «automatic execution ... was disabled» — штатное поведение Rigify, не ошибка.

**Что этим НЕ доказано:** пригодность auto-weights для реальных плеч/таза/доспехов;
fitted skeleton под пропорции произвольной модели (Rigify не Rig Fitter); корректность
осей/единиц/bind pose в Unity; воспроизводимость на моделях CubeGame (не запускались).

---

## PREP-02 — форматы и экспорт

```yaml
id: PREP-02
status: PLANNED
checks: []   # выполняется после PREP-01
note: |
  В PREP-01 уже проверен минимальный экспорт: FBX тестового ригнутого меша и обратный
  импорт в пустую сцену (см. выше). PREP-02 должен закрыть полный round-trip
  .blend/.fbx/.glb с масштабом, осями, материалами и анимационным action.
```

---

## PREP-03 — ComfyUI и локальная AI-инфраструктура

```yaml
id: PREP-03
status: PARTIAL        # установка и API-прогон доказаны; AI-модели и генерация 3D НЕ проверены
machine: WINDOWS_11
software: ComfyUI 0.45.0 (portable, official Comfy-Org release)
version: 0.45.0; python 3.13.14 (embedded); torch 2.14.1+cu130; CUDA runtime 13.0
source_url: https://github.com/Comfy-Org/ComfyUI/releases/download/v0.45.0/ComfyUI_windows_portable_nvidia.7z
license: GPL-3.0 (LICENSE в поставке; подтверждено по файлу репозитория v0.45.0)
install_location: D:\programs\ComfyUI  (portable, embedded python, 4.25 ГБ, 63 891 файл)
download_size: 2 071 479 423 Б (1.93 ГБ, .7z)
download_sha256: 60c12e8c7af778047ad0413722dd3dc0f6ca773a41cbf5cb229ee9bc92c44a6f
sha256_verified: YES (совпало с digest, опубликованным в GitHub release assets)
sample_asset: собственный минимальный граф EmptyImage → SaveImage (без чекпоинтов и весов)
command: |
  powershell -NoProfile -ExecutionPolicy Bypass -File "D:\Projects\CubeGame Factory\scripts\comfyui\prep03_run_smoke.ps1"
  powershell -NoProfile -ExecutionPolicy Bypass -File "...\prep03_run_smoke.ps1" -CpuMode
  # внутри: python_embeded\python.exe -s ComfyUI\main.py --windows-standalone-build --port 8188 `
  #            --disable-auto-launch --reserve-vram 5    (или --cpu)
input: |
  график из встроенных нод: EmptyImage(width=96, height=96, color=0x00C8FF) → SaveImage
  API-скрипт: scripts\comfyui\prep03_comfyui_smoke.py (только стандартная библиотека Python)
output: |
  outputs\comfyui\prep03_smoke_from_api.png                (96×96 PNG, скачан через /view)
  outputs\reports\prep03_comfyui_smoke_gpu_reserve5.json   (прогон GPU, reserve-vram 5)
  outputs\reports\prep03_comfyui_smoke_cpu.json            (прогон CPU)
  logs\PREP-03_run_gpu_2026-11-13.txt / PREP-03_run_cpu_2026-11-13.txt
  logs\PREP-03_cuda_sanity_2026-11-13.txt                  (matmul на CUDA встроенным torch)
  workflows\comfyui_prep03_smoke_api.json                  (граф для повторного запуска)
  серверная сторона: D:\programs\ComfyUI\ComfyUI\output\factoria_prep03_smoke_0000N_.png
checks:
  - name: Реальный запуск ComfyUI (GPU, --reserve-vram 5)
    result: PASS  (тёплый старт 10.8–11.8 с; первый холодный старт ~146 с)
  - name: Веб-интерфейс отдаётся
    result: PASS  (GET / → HTTP 200, 19 885 Б HTML, ComfyUI 0.45.0)
  - name: Python и зависимости рабочие
    result: PASS  (embedded python 3.13.14, torch 2.14.1+cu130, cuda_available=True, RTX 4060 Laptop, capability 8.9)
  - name: Минимальный workflow выполнен (без моделей)
    result: PASS  (prompt_id получен, /history → status_str=success, completed=true, 1.0 с)
  - name: Результат сохранён и скачан
    result: PASS  (96×96 PNG, 504 Б, /view 200; файл также есть в ComfyUI\output)
  - name: API-механизм (POST /prompt, /history, /view, /queue)
    result: PASS  (очередь пуста после выполнения)
  - name: CUDA-вычисления встроенным torch
    result: PASS  (matmul 2048×2048 за 0.12 с, пик allocated 56.1 МБ / reserved 68 МБ)
  - name: Генерация 3D-модели
    result: NOT_TESTED  (требуются веса AI-моделей — не скачивались без согласования)
issues:
  - первый холодный старт ~146 с (миграция SQLite-БД ComfyUI + скан ассетов), тёплый ~11 с
  - nvidia-smi на Windows/WDDM не отдаёт память процесса (compute-apps = 0) — VRAM мерилась по всей карте
  - граф без моделей не создаёт CUDA-тензоров: torch_vram_total = 0, прирост VRAM ≈ 80–90 МБ (инициализация)
next_action: >
  PREP-02 (форматы/экспорт) — следующий обязательный шаг. Для PREP-03 дальше требуется
  согласование конкретной AI-модели (источник, размер, лицензия, VRAM) и только затем
  тест реальной генерации/переработки геометрии.
```

**Измеренные величины (2026-11-13)**

| Метрика | GPU (`--reserve-vram 5`) | CPU (`--cpu`) |
|---|---|---|
| Готовность сервера (тёплый старт) | 10.8–11.8 с | 10.7–11.8 с |
| Выполнение workflow | 1.0 с | 1.0–1.02 с |
| Пиковый рабочий набор процесса ComfyUI | **972–973 МБ** | **858–860 МБ** |
| Свободная RAM до / минимум во время теста | 19.37 → 18.43 ГБ | 19.41 → 18.52 ГБ |
| Занятая VRAM всей карты до / пик | 1350 → 1436 MiB (**+86 MiB**) | 1348 → 1355 MiB (+7 MiB, шум) |
| RAM после теста | 19.45 ГБ | 19.43 ГБ |
| Общее время прогона (скрипт) | 14.4–15.1 с | 13.4–14.5 с |

**Карточка памяти локального AI (§4.1 AGENTS.md) — что измерено и что нет**

| Параметр | Факт |
|---|---|
| Название / версия | ComfyUI 0.45.0 portable NVIDIA (torch 2.14.1+cu130, CUDA 13.0) |
| Источник / лицензия | официальный GitHub release Comfy-Org/ComfyUI v0.45.0; GPL-3.0 |
| Вес / диск | архив 1.93 ГБ; установлено 4.25 ГБ; **генеративных чекпоинтов нет** (`models\checkpoints` пуст); в поставке 6 служебных TAESD-превью-кодеков ≈14 МБ — часть официальной сборки, нами не скачивались |
| Настройки запуска | `--reserve-vram 5` (резерв 5 ГБ из 8 ГБ VRAM → ComfyUI ≈ 3 ГБ), `--disable-auto-launch`, порт 8188; CPU-режим `--cpu` |
| RAM / VRAM | пик RAM процесса ≈ 0.97 ГБ; прирост VRAM ≈ 86 МБ на инициализацию; реальная нагрузка моделью **не измерена** |
| Время | холодный старт 146 с, тёплый 11 с, smoke-workflow 1.0 с |
| Выход / качество | PNG 96×96 (цвет 0x00C8FF) — доказан runtime, **не** качество генерации |
| Проблемы | нет OOM/подкачки; WDDM ограничивает per-process VRAM-метрику |
| Статус | **PARTIAL** — инфраструктура готова, пригодность AI-моделей не проверена |

**Чего этот тест НЕ доказывает:** способность генерировать 3D-модели, качество и лицензионную
чистоту AI-выходов, поведение VRAM под реальными моделями (SD/3D/motion), скорость на 8 ГБ VRAM,
пригодность для стиля CubeGame. Успешный API-прогон — это только «сервер и конвейер запускаются».

---
