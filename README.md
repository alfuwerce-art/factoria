# CubeGame Asset & Animation Factory Lab

Независимая лаборатория подготовки производственного конвейера: **переработка существующих моделей → оригинальные модели CubeGame** и **создание новых моделей с нуля**, далее геометрия → skeleton → rigging → skinning → новые анимации → экспорт для Unity.

**Сейчас этап PREP:** проверяются и подготавливаются готовые инструменты, а не пишутся собственные CubeGame-скрипты. Лаборатория изолирована от `D:\Projects\CubeGame`, исходной Alpha и `.scratch/content`.

---

## Состояние на 2026-11-13

| Пункт | Значение |
|---|---|
| PREP-00 (аудит ПК и ПО) | **READY_FOR_REVIEW** — выполнен, доказательства в `logs/PREP-00_detection_2026-11-13.txt` |
| Blender | **НЕ УСТАНОВЛЕН** → блокер PREP-01 |
| ComfyUI | **НЕ НАЙДЕН** (расхождение с ТЗ) → нужен путь от пользователя |
| Rigify | проверить после установки Blender |
| Git / remote | локальный репозиторий; remote **не настроен** (`PUSH=NOT_CONFIGURED`) |

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

Ожидаемый результат на этой машине: Python 3.13.14, Git 2.55.0, VS Code 1.145.2, Unity 6000.3.27f2/6000.6.7f1, Ollama 0.40.10, RTX 4060 Laptop 8188 MiB; **Blender отсутствует**.

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

**PREP-01:** скачать `blender-5.2.4-windows-x64.zip` (405 779 142 байта) и `.sha256` с `https://ftp.blender.org/release/Blender5.2/`, распаковать в `D:\programs\Blender\5.2\`, проверить SHA-256, GUI и `blender --background`, затем включить и проверить Rigify.
