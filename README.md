# CubeGame Asset & Animation Factory Lab

Независимая лаборатория подготовки производственного конвейера: **переработка существующих моделей → оригинальные модели CubeGame** и **создание новых моделей с нуля**, далее геометрия → skeleton → rigging → skinning → новые анимации → экспорт для Unity.

**Сейчас этап PREP:** проверяются и подготавливаются готовые инструменты, а не пишутся собственные CubeGame-скрипты. Лаборатория изолирована от `D:\Projects\CubeGame`, исходной Alpha и `.scratch/content`.

---

## Состояние на 2026-11-13

| Пункт | Значение |
|---|---|
| PREP-00 (аудит ПК и ПО) | **READY_FOR_REVIEW** — выполнен, доказательства в `logs/PREP-00_detection_2026-11-13.txt` |
| PREP-01 (Blender / Rigify / skinning / экспорт) | **READY_FOR_REVIEW** — Blender 5.2.4 LTS установлен и проверен, Rigify + auto weights + позы + FBX доказаны на собственной фигуре |
| Blender | **5.2.4 LTS** → `D:\programs\Blender\5.2\blender.exe` (SHA-256 сверен, PATH не менялся) |
| Rigify | **0.6.10**, встроенный; генерирует rig (160 deform + 546 control), skinning работает |
| ComfyUI | **НЕ НАЙДЕН** (расхождение с ТЗ) → нужен путь от пользователя |
| Git / remote | локальный репозиторий; remote **не настроен** (`PUSH=NOT_CONFIGURED`) |
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
scripts\                                   только диагностика и запуск smoke tests
outputs\{blender,rigging,animation,reports}
logs\                                      сырые доказательства запусков
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
масштаб и оси, материалы, дерево костей, веса, анимационный action; таблица `INPUT→OUTPUT` с потерями.
Минимальный FBX-экспорт уже проверен в PREP-01, но полный обмен форматами — ещё нет.
