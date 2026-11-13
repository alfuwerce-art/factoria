# CubeGame Asset & Animation Factory Lab

Независимая лаборатория подготовки производственного конвейера: **переработка существующих моделей → оригинальные модели CubeGame** и **создание новых моделей с нуля**, далее геометрия → skeleton → rigging → skinning → новые анимации → экспорт для Unity.

**Сейчас этап PREP:** проверяются и подготавливаются готовые инструменты, а не пишутся собственные CubeGame-скрипты. Лаборатория изолирована от `D:\Projects\CubeGame`, исходной Alpha и `.scratch/content`.

---

## Репозиторий и маршрутизация

- **GitHub:** [`alfuwerce-art/factoria`](https://github.com/alfuwerce-art/factoria) — отдельный репозиторий всего проекта Factory.
- **Ветки:** `main` — только утверждённая стабильная документация (исполнитель туда не пушит); `factory/work` — разработка, отчёты, скрипты, результаты испытаний и межчатовая память.
- **Маршрутизация чатов:** правило в [`CHAT_ROUTING.md`](CHAT_ROUTING.md). Префикс «мод» в запросе пользователя означает Factoria и запрещает чтение игрового CubeGame; без префикса — основная игра.
- **Исторический контекст:** исследования M1 из CubeGame сохранены в [`references/cubegame-m1/`](references/cubegame-m1/README.md) — это справка, а не текущая документация.
- **Миграция:** состояние переноса и оставшиеся шаги — [`docs/MIGRATION_STATUS.md`](docs/MIGRATION_STATUS.md).

---

## Состояние на 2026-11-13

| Пункт | Значение |
|---|---|
| PREP-00 (аудит ПК и ПО) | **READY_FOR_REVIEW** — выполнен, доказательства в `logs/PREP-00_detection_2026-11-13.txt` |
| PREP-01 (Blender / Rigify / skinning / экспорт) | **READY_FOR_REVIEW** — Blender 5.2.4 LTS установлен и проверен, Rigify + auto weights + позы + FBX доказаны на собственной фигуре |
| Blender | **5.2.4 LTS** → `D:\programs\Blender\5.2\blender.exe` (SHA-256 сверен, PATH не менялся) |
| Rigify | **0.6.10**, встроенный; генерирует rig (160 deform + 546 control), skinning работает |
| ComfyUI | **0.45.0 portable** → `D:\programs\ComfyUI\` (SHA-256 сверен, 4.25 ГБ); сервер/UI/API/workflow без моделей/CUDA проверены; **весов моделей нет** |
| Git / remote | `origin` = `alfuwerce-art/factoria.git`; рабочая ветка `factory/work`; `main` не изменяется исполнителем |
| Режим DSH | **CubeGame Factory** (`cubegame-factory`) — выбирается при создании нового чата |

**Начало работы в новом чате:** выберите режим **CubeGame Factory** и папку `D:\Projects\CubeGame Factory`; агент первым действием войдёт в неё и прочитает четыре документа в порядке AGENTS → 01 → 02 → 03.

Подробности: [`docs/TOOL_INVENTORY.md`](docs/TOOL_INVENTORY.md), [`docs/TEST_RESULTS.md`](docs/TEST_RESULTS.md), [`docs/PIPELINE_GAPS.md`](docs/PIPELINE_GAPS.md).

---

## Структура

```text
01_DEEPSEEK_FACTORY_IMPLEMENTATION_TZ.md   ТЗ: что разрешено, порядок, границы
02_FACTORY_OPERATIONAL_DESIGN.md           целевая архитектура конвейера
03_FACTORY_PROJECT_MEMORY.md               межчатовая память (обновляется после каждой задачи)
AGENTS.md                                  правила исполнителя
docs\                                      инвентарь, установки, лицензии, тесты, разрывы
environments\                              конфигурации окружений (без секретов)
manifests\                                 схемы входов/выходов
samples\original_test_assets\              собственные/открытые тестовые меши
samples\imported_results\                  результаты импорта
workflows\                                 workflow JSON (с учётом лицензий)
scripts\                                   только диагностика и запуск smoke tests (blender\, comfyui\)
outputs\{blender,rigging,animation,comfyui,reports}
logs\                                      сырые доказательства запусков
references\cubegame-m1\                    исторические материалы исследований M1 (справка)
workflows\                                 workflow JSON (с учётом лицензий)
```

---

## Как воспроизвести аудит PREP-00

```powershell
# консолидированный журнал обнаружения (Windows PowerShell 5.1)
# ключевые команды, полный вывод — в logs\PREP-00_detection_2026-11-13.txt
Get-CimInstance Win32_Processor | Select-Object Name,NumberOfCores,NumberOfLogicalProcessors
Get-CimInstance Win32_PhysicalMemory | Select-Object BankLabel,Capacity,Speed
nvidia-smi --query-gpu=name,driver_version,memory.total,memory.used,memory.free --format=csv
Get-Volume | Where-Object DriveLetter | Select-Object DriveLetter,@{n='Free_GB';e={[math]::Round($_.SizeRemaining/1GB,1)}}
Get-Command python,git,blender,ollama,node -ErrorAction SilentlyContinue
py -0p
```

Ожидаемый результат на этой машине: Python 3.13.14, Git 2.55.0, VS Code 1.145.2, Unity 6000.3.27f2/6000.6.7f1, Ollama 0.40.10, RTX 4060 Laptop 8188 MiB; Blender появился после PREP-01 в `D:\programs\Blender\5.2\`.

---

## Как воспроизвести ORC-02 (unattended pipeline на реальном Orc)

```powershell
# Одна команда: реальный источник CubeGame читается read-only, результат — в Factoria
python scripts\orc02\run_orc02.py --config scripts\orc02\configs\orc_profile.json `
    --out outputs\prototypes\orc_02\run1

# Детерминизм: повторный прогон даёт байт-идентичный GLB
python scripts\orc02\run_orc02.py --out outputs\prototypes\orc_02\run2

# Изменённая детализация (проверка, что конфиг влияет на геометрию)
python scripts\orc02\run_orc02.py --out outputs\prototypes\orc_02\alt --detail-scale 0.5

# Blender-валидация (headless): .blend, GLB round-trip, 3 вида
$env:BLENDER_USER_CONFIG="D:\Projects\CubeGame Factory\environments\blender\config"
& 'D:\programs\Blender\5.2\blender.exe' --background --factory-startup --python-exit-code 1 `
    --python "D:\Projects\CubeGame Factory\scripts\blender\orc02_validate.py" -- --run "outputs\prototypes\orc_02\run1"
```

Ожидаемый итог: `ORC02_OK … modules=16 boxes=487`, `ORC02_VALIDATION=PASS`, каталог
`outputs\prototypes\orc_02\run1\` с GLB, `descriptor.json`, `validation.json`, `.blend` и тремя PNG.
**Важно:** исходный Alpha-контент read-only и в git не публикуется; результат — `PARTIAL`
(см. `docs/tasks/ORC02_RUN_REPORT.md`), визуальной приёмки нет.

---
## Как воспроизвести PREP-03 (ComfyUI)

```powershell
# 1. Запуск ComfyUI + API smoke + замеры RAM/VRAM (GPU, резерв 5 ГБ из 8 ГБ VRAM)
powershell -NoProfile -ExecutionPolicy Bypass `
    -File "D:\Projects\CubeGame Factory\scripts\comfyui\prep03_run_smoke.ps1"

# 2. То же в RAM-first / CPU-режиме (VRAM не используется)
powershell -NoProfile -ExecutionPolicy Bypass `
    -File "D:\Projects\CubeGame Factory\scripts\comfyui\prep03_run_smoke.ps1" -CpuMode

# 3. Только CUDA-проверка встроенного torch (без сервера и моделей)
& 'D:\programs\ComfyUI\python_embeded\python.exe' -s `
    "D:\Projects\CubeGame Factory\scripts\comfyui\prep03_cuda_sanity.py"
```

Ожидаемый итог: `PREP03_RESULT=PASS`, отчёты `outputs\reports\prep03_comfyui_smoke_gpu_reserve5.json`
и `..._cpu.json`, PNG `outputs\comfyui\prep03_smoke_from_api.png` (96×96), логи `logs\PREP-03_*`.
Граф для повторного запуска: `workflows\comfyui_prep03_smoke_api.json`.
Консольный запуск вручную: `D:\programs\ComfyUI\run_nvidia_gpu.bat`; UI — `http://127.0.0.1:8188`.

---

## Как воспроизвести PREP-01 (Blender / Rigify / skinning / FBX)

```powershell
# 1. Проверка установки и версии (PATH не используется)
& 'D:\programs\Blender\5.2\blender.exe' --version

# 2. Изоляция пользовательского конфига Blender в лаборатории
$env:BLENDER_USER_CONFIG = 'D:\Projects\CubeGame Factory\environments\blender\config'

# 3. Headless smoke test: background + сохранение .blend
& 'D:\programs\Blender\5.2\blender.exe' --background --factory-startup --python-exit-code 1 `
    --python "D:\Projects\CubeGame Factory\scripts\blender\prep01_bg_smoke.py"

# 4. Полный тест: Rigify → generate rig → манекен → auto weights → позы → рендер → FBX → импорт
& 'D:\programs\Blender\5.2\blender.exe' --background --factory-startup --python-exit-code 1 `
    --python "D:\Projects\CubeGame Factory\scripts\blender\prep01_rigify_skinning.py"

# 5. GUI: открыть результат глазами
& 'D:\programs\Blender\5.2\blender.exe' "D:\Projects\CubeGame Factory\outputs\blender\prep01_rigify_skinned.blend"
```

Ожидаемый итог: `PREP01_RESULT=PASS`, отчёт `outputs\reports\prep01_rigify_skinning.json`,
файлы `outputs\blender\prep01_rigify_skinned.blend` / `.fbx` и два PNG-доказательства
(rest и control-поза). Полный прогон ≈ 12 с (11.8–12.0 с), пиковый рабочий набор 394–402 МБ, VRAM не используется
(рендер Cycles на CPU).

Официальные данные загрузки (проверено 2026-11-13):

| Файл | Размер (байт) | SHA-256 | Источник |
|---|---|---|---|
| `blender-5.2.4-windows-x64.zip` | 405 779 142 | `bbd78f8931dc940444da4ff2983374930f9f5c092ae0e330588e9760bb9d967c` | `https://download.blender.org/release/Blender5.2/` |
| `blender-5.2.4.sha256` | 777 | — | там же |

---

## Правила, которые нельзя нарушать

- Не изменять `D:\Projects\CubeGame`, Unity-сцены/prefab/assets, `main`, `integration/m0-all`.
- Не публиковать Alpha-ассеты и их производные.
- Не менять глобальные PATH/CUDA/драйверы/Python; только изолированные `venv`.
- Не покупать платное ПО и не скачивать тяжёлые AI-веса без согласования (источник, размер, лицензия, VRAM, место).
- Не объявлять этап завершённым по факту установки или exit code 0 — нужен воспроизводимый полезный результат.

Полные правила — `AGENTS.md`.

---

## Следующий шаг

**PREP-02:** round-trip форматов на собственной модели — `.blend` / `.fbx` / `.glb`: импорт и экспорт,
масштаб и оси, материалы, дерево костей, веса, анимационный action; таблица `INPUT→OUTPUT` с потерями,
и отдельно — как получить deform-only скелет вместо 706-костного control rig.
Минимальный FBX-экспорт уже проверен в PREP-01, ComfyUI-инфраструктура готова (PREP-03 `PARTIAL`),
но полный обмен форматами — ещё нет.
