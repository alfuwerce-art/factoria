# INSTALLATION_LOG — CubeGame Factory Lab

**Ведётся с:** 2026-11-13
**Правило:** одна строка = один факт установки/загрузки с источником, лицензией и причиной. Планы — в конце файла, они не считаются установкой.

---

## 1. Установки, выполненные DeepSeek

| # | Дата | Инструмент | Версия | Источник | Лицензия | Куда | Причина | Результат |
|---|---|---|---|---|---|---|---|---|
| 1 | 2026-11-13 | **Blender** | **5.2.4 LTS** (build cd5dc428cce1, 2026-11-10) | `https://download.blender.org/release/Blender5.2/blender-5.2.4-windows-x64.zip` (405 779 142 Б) + `.sha256` | GPL-2.0-or-later | `D:\programs\Blender\5.2\` (портативно, zip) | ядро конвейера: геометрия, armature, skinning, анимация, CLI, FBX | **INSTALLED + SMOKE_PASS** — SHA-256 совпал, `--version` OK, GUI OK, headless OK, Rigify+skinning+FBX проверены (`logs\PREP-01_*`) |

**Проверка целостности загрузки:**

| Параметр | Значение |
|---|---|
| Файл | `blender-5.2.4-windows-x64.zip`, 405 779 142 байт |
| SHA-256 опубликованный (`blender-5.2.4.sha256`, строка `windows-x64.zip`) | `bbd78f8931dc940444da4ff2983374930f9f5c092ae0e330588e9760bb9d967c` |
| SHA-256 вычисленный (`Get-FileHash -Algorithm SHA256`) | `BBD78F8931DC940444DA4FF2983374930F9F5C092AE0E330588E9760BB9D967C` |
| Совпадение | **ДА** |
| Распаковка | `tar.exe -xf <zip> -C "D:\programs\Blender\5.2" --strip-components=1` (3.2 с) |
| Установлено | 901.3 МБ, 6530 файлов; каталог `D:\programs\Blender\5.2\` |
| PATH | **не изменялся** (проверено `Machine`/`User` PATH — Blender отсутствует) |
| Изоляция конфигурации | `BLENDER_USER_CONFIG=D:\Projects\CubeGame Factory\environments\blender\config` |
| Установщик файла | `D:\programs\_installers\` (локально, в git не попадает: `*.zip`) |

---

## 2. Создание лабораторной среды (не установка ПО)

| Дата | Действие | Результат |
|---|---|---|
| 2026-11-13 | Проверено отсутствие `D:\Projects\CubeGameFactoryLab` | каталог отсутствовал |
| 2026-11-13 | Создана структура каталогов по ТЗ §4 (`docs`, `environments`, `manifests`, `samples\{original_test_assets,imported_results}`, `workflows`, `scripts`, `outputs\{blender,rigging,animation,reports}`, `logs`) | создано |
| 2026-11-13 | Скопированы 4 документа из `D:\Projects\CubeGame Factory` | SHA-совпадение подтверждено для всех четырёх |
| 2026-11-13 | Записан журнал обнаружения `logs/PREP-00_detection_2026-11-13.txt` | 177 строк, реальный вывод команд, UTF-8 |
| 2026-11-13 | Локальный git-репозиторий инициализирован (без remote) | `main` = документация, `factory/work` = работа; `PUSH=NOT_CONFIGURED` |
| 2026-11-13 | Рабочая папка сведена к `D:\Projects\CubeGame Factory` (перенос журналов, доказательств и git-истории; `CubeGameFactoryLab` → архив) | действующий каталог проекта |
| 2026-11-13 | Установлен пользовательский режим DSH **CubeGame Factory** (`@local/cubegame-factory-preset`, база Standard) | `plugins\cubegame-factory-preset\`, строка `include:preset-cubegame-factory` активна |

---

## 3. Уже установленное ПО, обнаруженное на машине (не устанавливалось мной)

| Компонент | Версия | Путь | Статус |
|---|---|---|---|
| Python | 3.13.14 | `C:\Users\bow\AppData\Local\Programs\Python\Python313\python.exe` | DETECTED |
| Python | 3.14.6 | `C:\Users\bow\AppData\Local\Python\pythoncore-3.14-64\python.exe` | DETECTED |
| Git | 2.55.0 | `C:\Program Files\Git\cmd\git.exe` | DETECTED, identity НЕ настроена |
| VS Code | 1.145.2 | `C:\Users\bow\AppData\Local\Programs\Microsoft VS Code\bin\code.cmd` | DETECTED |
| Unity Hub | 3.22.5 | `D:\Unity Hub\Unity Hub.exe` | DETECTED_NOT_TESTED |
| Unity Editor | 6000.3.27f2 | `D:\Unity\Hub\Editor\6000.3.27f2\Editor\Unity.exe` | DETECTED_NOT_TESTED |
| Unity Editor | 6000.6.7f1 | `D:\Unity\6000.6.7f1\Editor\Unity.exe` | DETECTED_NOT_TESTED |
| Ollama | 0.40.10 | `C:\Users\bow\AppData\Local\Programs\Ollama\ollama.exe` | DETECTED_NOT_RUNNING |
| .NET Runtimes | 7.0.14 / 8.0.34 | `C:\Program Files\dotnet\` | DETECTED |
| WinRAR | 7.13 | `C:\Program Files\WinRAR` | DETECTED |
| NVIDIA драйвер | 610.47 | system | DETECTED (CUDA UMD 13.3, Toolkit отсутствует) |

---

## 4. Известные риски установок

| Риск | Влияние | Мера |
|---|---|---|
| Установка Blender «второй копией» при наличии переносимой | рассинхрон версий, лишний ГБ | сначала проверить переносимую/D:-установку; ставить один раз |
| Изменение глобального PATH | ломает другие проекты и Unity | PATH не менять; вызывать Blender по абсолютному пути |
| Скачивание AI-весов до проверки лицензии/VRAM | место, правовые риски, OOM | сначала `LICENSE_MATRIX` + замер VRAM, веса — только по согласованию |
| Установка ComfyUI «с нуля» при существующей у пользователя | дубликат, конфликт портов | сначала получить фактический путь от пользователя |
| Установка n8n | требует Node.js, отдельной службы, устойчивой лицензии | не ставить без доказанного выигрыша над Python (`PIPELINE_GAPS.md`) |
| Заполнение C: (68 ГБ) | срыв обновлений Windows/Unity | всё тяжёлое — на D: |

---

## 5. План установок (частично выполнено)

Порядок соответствует ТЗ §3 и §10 (`PREP-00 → PREP-01 → PREP-02`).

| Шаг | Инструмент | Действие | Условие запуска |
|---|---|---|---|
| PREP-01 | **Blender LTS** | **ВЫПОЛНЕНО 2026-11-13:** официальный zip 5.2.4 LTS, SHA-256 сверен, распакован в `D:\programs\Blender\5.2\` | — |
| PREP-01 | **Rigify** | **ВЫПОЛНЕНО:** встроенный аддон 0.6.10 включён через `bpy.ops.preferences.addon_enable`, риг сгенерирован на собственной фигуре, skinning и контрольные позы проверены | — |
| PREP-01 | **venv** | **НЕ ВЫПОЛНЕНО ОСОЗНАННО:** Blender несёт собственный Python 3.13.13; внешний Python-раннер появится только на PREP-02 (`scripts\` сейчас — только Blender-диагностика). Пустой venv не создавался, чтобы не плодить артефакты | при первом внешнем Python-скрипте |
| PREP-02 | обмен форматами | `.blend`/`.fbx`/`.glb` round-trip на собственном меше; в PREP-01 уже проверен минимальный FBX-экспорт + обратный импорт | следующий шаг |
| PREP-03 | **ComfyUI** | получить фактический путь у пользователя; при отсутствии — согласовать установку | блокер: установка не найдена |
| PREP-05 | **Cascadeur** | изучить лицензию и системные требования; установка только при приемлемых условиях | после проверки лицензии |
| — | n8n | не устанавливать | требуется доказательство преимущества |

**Согласования, которые нужны от пользователя:**
1. Фактический путь ComfyUI (или решение, что его нужно установить заново).
2. URL отдельного GitHub-репозитория Factory (публикация `factory/work`).
3. Позже: любые AI-веса (размер, лицензия, VRAM) — отдельно.
