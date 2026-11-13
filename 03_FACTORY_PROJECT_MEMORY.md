# CubeGame Asset & Animation Factory Lab — межчатовая память

**Документ:** `03_FACTORY_PROJECT_MEMORY.md`  
**Версия:** 1.6 · 13.11.2026  
**Статус:** `PREP-00 = READY_FOR_REVIEW`, `PREP-01 = READY_FOR_REVIEW` (Blender/Rigify/skinning/FBX доказаны), **`PREP-03 = PARTIAL`** (ComfyUI установлен, runtime/API проверены; AI-модели не тестировались), **`ORC-01 = READY_FOR_REVIEW`** (технический прототип проверен в Blender, художественной приёмки нет), PREP-02 не начат. GitHub-миграция в `alfuwerce-art/factoria` выполнена и проверена.  
**Рабочая папка (действующая):** `D:\Projects\CubeGame Factory\` — единый канонический каталог проекта. Содержит четыре документа, `CHAT_ROUTING.md`, журналы `docs/`, доказательства `logs/`, скрипты `scripts/`, выходы `outputs/`, `references/cubegame-m1/`, `workflows/`, пресет `plugins/` и git-репозиторий (ветки `main` / `factory/work`, remote `origin` = Factoria). Ранее созданный `D:\Projects\CubeGameFactoryLab` **SUPERSEDED**: архив прошлой сессии.  
**Исполнитель:** DeepSeek Harness.  
**Назначение:** сохранять между чатами фактическое состояние независимой Factory Lab, утверждённые решения, установки, результаты тестов, проблемы и точку продолжения. **Этот файл обновляется исполнителем после каждого завершённого пакета работы и перед передачей в другой чат.** Обязательные правила исполнителя находятся в `AGENTS.md` (четвёртый служебный файл, а не замена одного из трёх основных документов).

---

## 0. Правила начала каждой новой сессии

1. Сначала прочитать `AGENTS.md`, затем **три основных документа** в папке проекта:
   - `01_DEEPSEEK_FACTORY_IMPLEMENTATION_TZ.md` — **что разрешено делать и в каком порядке**;
   - `02_FACTORY_OPERATIONAL_DESIGN.md` — **как должна работать Factory и какая итоговая цель**;
   - `03_FACTORY_PROJECT_MEMORY.md` — **что уже сделано, что утверждено, что не сделано и какой следующий шаг**.
2. Проверить реальные файлы и программы на диске. **Не доверять памяти, если файлы или установленная программа отсутствуют.**
3. Сверить текущий этап, установленные инструменты и запреты в разделах ниже. Продолжать с первого незавершённого шага; не устанавливать ничего повторно без основания.
4. Перед действиями вне оговорённых ограничений запросить разрешение пользователя. Не считать план разрешением на скачивание тяжёлых моделей, платные покупки, изменение PATH, CUDA/драйверов или CubeGame.
5. После работы обновить **сначала проверяемые журналы** (версии, команды, результаты тестов), затем краткую межчатовую память. Указать дату, статус, факты, ссылки на evidence и следующий конкретный шаг.
6. Не изменять утверждённые производственные решения молча: новые идеи маркировать `PROPOSAL`, реализованные без приёмки — `EXPERIMENTAL`, проверенные — `SMOKE_PASS`/`TESTED`; приёмка принадлежит пользователю.

**При конфликте:** явное новое решение пользователя → ТЗ (документ 01) → целевая архитектура (02) → эта память (03) → устаревшие отчёты. При изменении решения синхронизировать все три документа.

## 1. Цель и границы проекта

**Долгосрочная цель:** независимая локальная система, в которой:

- поток A: изученная существующая модель каталога Unity → существенно **оригинально переработанная** модель CubeGame;
- поток B: **совершенно новая** модель из оригинального концепта через Blender/процедурные и/или AI-инструменты;
- затем **общая цепочка**: готовая геометрия → класс анатомии и landmarks → compatible skeleton → rig fitting → control rig → skinning/attachments → новые либо повторно используемые анимации → характерная анимационная индивидуальность → экспорт/валидация → готовность к официальной Unity-интеграции;
- после каждой сопоставимой партии `1 → 2 → 5 → 10 → 25 → 50 → batch` — выявление повторяющихся ошибок, исправление **общего правила**, проверка регрессий и сокращение ручных технических правок на один утверждённый ассет. **Числовые условия перехода между партиями НЕ установлены.**

**Текущая цель PREP:** по очереди проверить и подготовить инструменты, лицензии, окружения, демонстрационные smoke tests, схемы обмена; НЕ разрабатывать пока CubeGame-specific Rig Fitter, Animation Resolver, большие Blender Python пайплайны, и НЕ переделывать реальные игровые модели. Код допускается только для минимальной диагностики/запуска тестов, как разрешено ТЗ.

**Жёсткая изоляция:** не изменять `D:\Projects\CubeGame`, Unity runtime, игровые модели/сцены, сохранения, `integration/m0-all` или `main`, исходную Alpha и `.scratch/content`. Временно использовать собственные/лицензированные тестовые меши. Исходные Alpha-ассеты не публиковать. Дальнейший импорт в CubeGame — отдельный этап и разрешение.

## 2. Три документа — единственный основной контекст лаборатории

| Документ | Роль | Когда обновлять |
|---|---|---|
| `01_DEEPSEEK_FACTORY_IMPLEMENTATION_TZ.md` | Обязательные задачи, разрешения, ограничения, порядок установки, ожидаемые результаты | Только по решению пользователя или согласованному изменению плана |
| `02_FACTORY_OPERATIONAL_DESIGN.md` | Целевая архитектура двух потоков, интерфейсы модулей, критерий готового ассета | При утверждённых архитектурных изменениях; не переписывать под каждую неудачу |
| `03_FACTORY_PROJECT_MEMORY.md` | Межчатовое состояние, факты, решения, прогресс и точки продолжения | **В конце каждой рабочей сессии/этапа** и до смены чата |

Дополнительные журналы и отчёты (`docs/TOOL_INVENTORY.md`, `docs/INSTALLATION_LOG.md`, `docs/TEST_RESULTS.md`, `docs/LICENSE_MATRIX.md`, `docs/PIPELINE_GAPS.md`) — **доказательная база**, а не четвёртый конкурирующий главный документ. В памяти должны быть ссылки на них.

## 3. Утверждённые исходные решения

| ID | Решение | Статус |
|---|---|---|
| FACT-D01 | Factory Lab создаётся **вне основного CubeGame**, предпочтительно `D:\Projects\CubeGameFactoryLab` | APPROVED USER DIRECTION |
| FACT-D02 | Основные документы — **три**: ТЗ, целевая технология, межчатовая память | APPROVED USER DIRECTION |
| FACT-D03 | Сейчас сначала последовательно готовим и тестируем готовые инструменты; специальные CubeGame-скрипты Blender и собственные runtime-модули откладываем | APPROVED USER DIRECTION |
| FACT-D04 | Приоритет: переработка уже существующих моделей; новые создаём вторым производственным потоком | APPROVED |
| FACT-D05 | Геометрия сначала, затем fitted skeleton/rigging/skinning и новые animation packages; требования к движениям планируются заранее | APPROVED |
| FACT-D06 | Общие rig/anatomy contracts и базовые animation packages + обязательная **индивидуальность** видов в движении | APPROVED |
| FACT-D07 | Масштабирование `1→2→5→10→25→50→batch`, при этом цель — меньше ручных правок; числовые условия переходов пока не определять | APPROVED |
| FACT-D08 | Не устанавливать платные инструменты и крупные AI-веса без согласия; локальный GPU 8 GB VRAM, использовать последовательные задачи | APPROVED SCOPE |
| FACT-D09 | Этап M1 основного CubeGame не открыт; лабораторный PREP не даёт права менять Unity/runtime | APPROVED SCOPE |
| FACT-D10 | Rigify/Blender/Unity — готовые инструменты; Python — способ автоматизации; n8n, AI motion, autorig — кандидаты, а не уже одобренный обязательный стек | PROPOSED TOOL SET |
| FACT-D11 | Отдельный GitHub-репозиторий Factory используется для отчётности и кода: `main` — стабильная документация, `factory/work` — единственная повседневная рабочая ветка. URL remote ещё не указан; не выдумывать. | APPROVED USER DIRECTION |
| FACT-D12 | Главный критерий — фактический сквозной работоспособный результат, а не число установок/файлов/отчётов. См. AGENTS.md §9 и §10. | APPROVED USER DIRECTION |
| FACT-D13 | Канонический каталог лаборатории — `D:\Projects\CubeGameFactoryLab` (создан 2026-11-13). Папка `D:\Projects\CubeGame Factory` (с пробелом) — только источник документов, не рабочая. | SUPERSEDED by FACT-D16 |
| FACT-D14 | Нумерация этапов берётся из ТЗ (01) — PREP-00…PREP-07. Прежний индекс памяти v1.1 (PREP-00…PREP-12) помечен SUPERSEDED, история не удалена. | EXECUTED (PREP-00) |
| FACT-D15 | В DSH создан отдельный выбираемый режим **CubeGame Factory** (id `cubegame-factory`, пресет-бандл `@local/cubegame-factory-preset` на базе Standard, без изменения встроенных пресетов). | EXECUTED (2026-11-13) |
| FACT-D16 | Единственная рабочая папка проекта — `D:\Projects\CubeGame Factory`. `D:\Projects\CubeGameFactoryLab` — архив прошлой сессии. Пути в AGENTS.md приведены к фактическому каталогу. | APPROVED USER DIRECTION |

- **FACT-D17 (2026-11-13):** [одна эталонная модель → визуальная приёмка владельца → прототип эмоций → отдельная приёмка → масштабирование](docs/decisions/FACT-D17-character-visual-first-face-emotions.md). Ключевой стандарт: более индивидуальное и выразительное пиксельное лицо (+≈2 субъективных пункта детализации), без мультяшности; кубические раздельные конечности и будущие плечо/предплечье/кисть, бедро/голень/стопа. Дизайн утверждён как порядок будущего прототипа; модель ещё не изготовлена, эмоции не реализованы. **Бюджет будущей AI-задачи: максимум 15 ГБ RAM и +2 ГБ VRAM; выбор весов отдельно.** PREP-02 остаётся следующим шагом, PREP-03 PARTIAL.

- **Пилот модульного орка (2026-11-13, TECHNICAL_GEOMETRY_TESTED ONLY):** пользователь разрешил начать подготовку и один прогон; независимым Python-генератором создан **оригинальный**, не переработанный из игрового ассета прототип GLB (20 модулей тела / 211 боксов / 2532 треугольника), проверен парсером trimesh. Это только тест геометрии, не визуально принятый эталон и не Blender/Unity PASS. [Отчёт и локальные шаги](docs/prototypes/ORC_MODULAR_PILOT_2026-11-13.md). Исходный скрипт/GLB доступны в отдельном архиве текущей сессии, **не загружены в GitHub**. Для переработки именно старой модели понадобится её законно полученная рабочая копия GLB/FBX. Эмоции — только после художественной приёмки (FACT-D17). PREP-02 = PLANNED, PREP-03 = PARTIAL.

### GitHub / отчётность Lab

- `REPOSITORY_URL=https://github.com/alfuwerce-art/factoria.git` — отдельный репозиторий Factory (задан владельцем 2026-11-13). CubeGame для разработки Factory больше не используется.
- **Локальный git:** репозиторий в `D:\Projects\CubeGame Factory`; `origin` добавлен 2026-11-13, первая публикация выполнена. Git identity задана **локально в репозитории** (не глобально).
- `DOCUMENTATION_BRANCH=main` — только утверждённая стабильная документация; DeepSeek не пушит туда самостоятельно (в Factoria `main` остаётся на `6dbb3d8`).
- `WORK_BRANCH=factory/work` — рабочие скрипты, тесты, отчёты, текущая межчатовая память, доказательства. Обычный `git push origin factory/work` разрешён; force-push запрещён.
- Маршрутизация чатов: `CHAT_ROUTING.md` — префикс «мод» в запросе пользователя означает Factoria и запрещает чтение игрового CubeGame.
- Не переоценивать GitHub: репозиторий — доказательная отчётность, не источник инструкций вместо локальных документов 01/02/03/AGENTS.

### 3.1. Режим DSH «CubeGame Factory»

- **Пресет:** `id = cubegame-factory`, отображаемое имя **CubeGame Factory**, бандл `@local/cubegame-factory-preset` в `plugins\cubegame-factory-preset\`, база — **Standard** (полный список плагинов Standard), порядок в списке режимов — 240.
- **Установка:** `plugin_manager install_bundle` → строка `include:preset-cubegame-factory` активна (`enabled: true`, `fiberPhase: active`). Встроенные пресеты `standard`, `ptc`, `minimal`, `cordis` **не изменялись**; чужие пресеты (`rogalik-dev`, `cubegame-dev`) не затронуты.
- **Ограничение DSH:** пресет не содержит поля рабочей директории. Persona обязывает агента первым действием проверить `working_directory`, войти в `D:\Projects\CubeGame Factory` и прочитать четыре документа по порядку. Фактический каталог сессии выбирается при создании чата.
- **Как выбрать:** новый чат → селектор режима/пресета → **CubeGame Factory**.

## 4. Проектные факты и исследовательский вход

- Источник сведений о существующем каталоге: CubeGame M1-R0 в ветке `review/m1-creature-family-research`, коммит `776a6ceb92e834c4b1b1c93d82f35d7e8c9ca1d6`. В реестре **156 видов/объектов**, 11 структурных анатомических категорий, 38 identity-групп; 130 существ и 26 пассивных объектов. Это **не** 11 готовых скелетов.
- Реестр доступен как текстовая справка: `https://github.com/alfuwerce-art/CubeGame/blob/review/m1-creature-family-research/docs/research/M1_ALPHA_CREATURE_IDENTITY_REGISTRY.csv`. Не копировать закрытый исходный контент Alpha в Lab.
- Соответствие `Alpha kind → подготовленный Unity visual` по данным M1-R0 установлено в реестре; геометрия/клипы находятся локально (`LOCAL_ONLY`) и не являются универсально доступными FBX-ассетами. Нельзя заявлять их наличие в отдельной лаборатории.
- **ПОДТВЕРЖДЕНО АУДИТОМ 2026-11-13 (PREP-00):** Windows 11 Pro 10.0.26200 x64; AMD Ryzen 5 7535HS 6C/12T; 32 ГБ (2×16 DDR5-5600, доступно ОС 31.24 ГБ); **NVIDIA RTX 4060 Laptop 8188 MiB VRAM**, драйвер 610.47, CUDA UMD 13.3, свободно 6706 MiB; C: 68.2 ГБ свободно / D: 642.1 ГБ свободно. Evidence: `logs/PREP-00_detection_2026-11-13.txt`.
- **УСТАНОВЛЕНО 2026-11-13 (PREP-01):** **Blender 5.2.4 LTS** (build `cd5dc428cce1`, 2026-11-10, внутренний Python 3.13.13) из официального zip `blender-5.2.4-windows-x64.zip` (405 779 142 Б), SHA-256 `bbd78f8931dc940444da4ff2983374930f9f5c092ae0e330588e9760bb9d967c` **совпал** с опубликованным. Распаковано портативно в `D:\programs\Blender\5.2\` (901.3 МБ, 6530 файлов). PATH не менялся, установщик не использовался. Пользовательский конфиг изолирован: `BLENDER_USER_CONFIG=D:\Projects\CubeGame Factory\environments\blender\config`. Evidence: `logs/PREP-01_rigify_skinning_2026-11-13.txt`, `logs/PREP-01_isolation_2026-11-13.txt`.
- **Blender add-ons (факт, 5.2.4):** Rigify **0.6.10**, io_scene_fbx **5.15.0**, io_scene_gltf2 **5.2.41** — все встроенные (`5.2\scripts\addons_core\`), отдельной загрузки не требуют. Evidence: `logs/PREP-01_diagnostics_2026-11-13.txt`.
- **Измерено в PREP-01:** полный прогон Rigify+skinning+FBX — **11.8–12.0 с** (два прогона), пиковый рабочий набор процесса Blender **394–402 МБ**, свободная RAM 20.43 → 20.45 ГБ, рендер Cycles **на CPU** (VRAM не занималась). Риг: metarig 159 костей → rig 706 (160 DEF + 546 control). Манекен: 1280 вершин (160 оболочек) → voxel remesh → 3926 вершин, 1 оболочка. Веса: 160 групп, 0 вершин без весов, но сумма весов 0.732–0.9999 (не нормирована). Деформация: IK 0.562 м, FK 0.332 м, прямой DEF 0.0 м. FBX 1.54 МБ → обратный импорт: 706 костей, 145 vgroups, деформация 0.566 м.
- **GitHub (Factoria) 2026-11-13:** remote `origin` = `https://github.com/alfuwerce-art/factoria.git`. Истории локальная и удалённая были **не связаны** (`merge-base` пуст) — объединено через `git merge origin/factory/work --allow-unrelated-histories`; конфликт был только в `README.md` (add/add), взят локальный README + добавлен раздел о маршрутизации. Merge-коммит `8395409`, push `ca5bfef..8395409`; проверено: `HEAD == origin/factory/work`, `git diff` пустой, на remote 47 файлов. `main` в Factoria не изменялся.
- **УСТАНОВЛЕНО 2026-11-13 (PREP-03):** **ComfyUI 0.45.0 portable NVIDIA** из официального GitHub release (`.7z`, 2 071 479 423 Б, SHA-256 `60c12e8c…a6f` совпал) → `D:\programs\ComfyUI\` (4.25 ГБ, 63 891 файл, изолированный `python_embeded` 3.13.14, torch **2.14.1+cu130**, CUDA runtime 13.0). Распаковано официальным `7zr.exe` 26.04 (public domain, один файл в `D:\programs\_installers\`). PATH и системный Python не менялись, CUDA Toolkit не ставился, **генеративные веса не скачивались** (`models\checkpoints` пуст; в поставке 6 служебных TAESD-превью ≈14 МБ).
- **Измерено в PREP-03:** тёплый старт сервера 10.7–11.8 с, **первый холодный старт ~146 с** (миграция SQLite + скан ассетов); smoke-граф `EmptyImage → SaveImage` без моделей — 1.0 с, PNG 96×96 сохранён и скачан через `/view`. Пик RAM процесса ComfyUI **972 МБ** (GPU-режим) / **859 МБ** (CPU-режим), свободная RAM 19.4 → минимум 18.4 ГБ. Прирост VRAM всей карты при инициализации **≈ +86 МБ** (nvidia-smi на WDDM не отдаёт per-process память). CUDA-проверка встроенного torch: RTX 4060 Laptop, capability 8.9, matmul 2048² за 0.12 с, пик allocated 56.1 МБ / reserved 68 МБ.
- **ORC-01 (2026-11-13):** переданный архив найден как `C:\Users\bow\Downloads\FACTORIA_ORC_01_package.zip` (78 966 Б, SHA-256 `db27a186…2c1d`) — имя отличалось от `factoria_orc_prototype.zip`, содержимое совпало с описанием пилота. Генератор `scripts/voxel/orc_prototype.py` (stdlib) отработал локально за **0.18 с / 12.9 МБ RAM**: 211 боксов, 20 модулей, 2532 треугольника, 1688 вершин, GLB 71 904 Б. **Повторяемость:** два прогона с seed 17 дают одинаковый SHA-256; исходный (до правок) генератор воспроизвёл переданный GLB **байт-в-байт** (`a6b0b871…dd3e`); seed 23 даёт другой файл.
- **ORC-01 дефекты (найдены и минимально исправлены):** (1) 4 стыка конечностей без зазора (боксы `upper_arm↔forearm` L/R и `shin↔foot` L/R пересекались) — подняты/уменьшены висячие кубы и сдвинута голень; (2) `COLOR_0` в GLB без `"normalized": true` — Blender читал все цвета как белые; флаг добавлен. После правок: 0 issues у сгенерированного GLB, зазоры 0.020–0.045 м, 60 различных RGBA8.
- **ORC-01 проверка в Blender 5.2.4:** импорт 20 независимых mesh-объектов (0.1 с), 1688 вершин/2532 треугольника, вырожденных граней нет, 1 материал `voxel_vertex_colors` (unlit: Color Attribute → Emission), габариты 2.09 × 0.9357 × 3.13 м (Y-up → Z-up корректен), сдвиг `forearm_L` не двигает другие модули (дельта 0.0 м), `.blend` 118 424 Б сохранён и **переоткрыт**, GLB round-trip без потерь (20 объектов, 2532 треугольника, позиции вершин совпадают, цвета сохранены), три вида отрендерены (Cycles CPU). Ресурсы: пик RAM Blender **281–315 МБ**, VRAM не расходовалась.
- **Обнаруженное ПО (факт, версии и пути):** Python 3.13.14 (`C:\Users\bow\AppData\Local\Programs\Python\Python313\python.exe`, в PATH по умолчанию; второй 3.14.6 через `py`), pip 26.1.2, Git 2.55.0, VS Code 1.145.2, Unity Hub 3.22.5, Unity **6000.3.27f2** (`D:\Unity\Hub\Editor\6000.3.27f2\Editor\Unity.exe`) и 6000.6.7f1, Ollama 0.40.10 (не запущен), .NET 7/8, WinRAR 7.13.
- **Отсутствует (подтверждено поиском на PREP-00, актуально с оговорками):** Blender и ComfyUI **установлены 2026-11-13** (см. ниже); по-прежнему отсутствуют Cascadeur, n8n, системный Node.js/npm/pnpm, ffmpeg в PATH, CUDA Toolkit (`nvcc`), 7-Zip (запись в реестре устарела — используется отдельный `7zr.exe`).
- **ComfyUI (актуально 2026-11-13):** старый экземпляр был удалён владельцем; выполнена новая установка с нуля — официальный portable 0.45.0 NVIDIA в `D:\programs\ComfyUI\`, SHA-256 сверен, runtime/API проверены (PREP-03 `PARTIAL`).
- **Ловушки среды:** `python3.exe` в PATH — заглушка Microsoft Store (не использовать); глобальный Python содержит 47 сторонних пакетов, но **без torch/numpy** (чистая база, отдельный venv обязателен); shell — Windows PowerShell **5.1** (нет pwsh 7), `Tee-Object` пишет UTF-16 → перекодировать в UTF-8. Git identity на 2026-11-13 задана локально в репозитории.
- Unity 6000.3 LTS, VS Code, Ollama и DeepSeek Harness пользователь использует; версии подтверждены. ComfyUI установлен 2026-11-13 (0.45.0 portable).
- Не смешивать интеллект существа с skeleton archetype: примитивный человекоподобный и разумный гуманоид могут разделять скелет, но отличаются дизайном/анимационной индивидуальностью.
- Не считать Alpha-анимации итоговой целью: новый CubeGame combat требует **новых** боевых motion clips и проверенной синхронизации с gameplay.

## 5. Фактический прогресс подготовки (обновляется DeepSeek)

**Последняя проверка состояния:** 2026-11-13 12:30 MSK, PREP-01 выполнен на реальной машине (Blender установлен и проверен), доказательства сохранены.

**Нумерация синхронизирована с ТЗ (документ 01, §5).** Прежний индекс памяти `PREP-00…PREP-12` (v1.1) **SUPERSEDED**: он дробил этапы иначе и расходился с ТЗ. Действующая последовательность — PREP-00 → PREP-07 по ТЗ:

| Этап (ТЗ) | Назначение | Статус | Evidence/путь |
|---|---|---|---|
| **PREP-00** | Аудит ПК, ПО, дисков, лицензий до загрузок | **READY_FOR_REVIEW** | `logs/PREP-00_detection_2026-11-13.txt`, `docs/TOOL_INVENTORY.md`, `docs/INSTALLATION_LOG.md`, `docs/LICENSE_MATRIX.md` |
| **PREP-01** | Blender: установка/версия, GUI + background; Rigify: add-on, metarig, generate rig на собственной фигуре; встроенные Armature Modifier / Automatic Weights; экспорт | **READY_FOR_REVIEW** (все операции SMOKE_PASS) | `logs/PREP-01_rigify_skinning_2026-11-13.txt`, `logs/PREP-01_headless_smoke_2026-11-13.txt`, `logs/PREP-01_diagnostics_2026-11-13.txt`, `logs/PREP-01_isolation_2026-11-13.txt`, `outputs/reports/prep01_rigify_skinning.json`, `outputs/blender/prep01_rigify_skinned.blend/.fbx`, `outputs/blender/prep01_rest_pose.png`, `outputs/blender/prep01_control_pose.png`, `outputs/blender/prep01_gui_open.png`, `docs/TEST_RESULTS.md` |
| **PREP-02** | Обмен форматами `.blend`/`.fbx`/`.glb`: import/export, масштаб, оси, материалы, кости, веса, анимация | `PLANNED` | минимальный FBX-экспорт уже проверен в PREP-01 |
| **PREP-03** | ComfyUI и локальные модели геометрии (≥2 подхода, 3D-to-3D отдельно от image-to-3D) | `PARTIAL` — установка + runtime/API smoke PASS; модели и 3D-генерация не тестировались | `logs/PREP-03_run_gpu_2026-11-13.txt`, `logs/PREP-03_run_cpu_2026-11-13.txt`, `logs/PREP-03_cuda_sanity_2026-11-13.txt`, `outputs/reports/prep03_comfyui_smoke_*.json`, `outputs/comfyui/prep03_smoke_from_api.png`, `workflows/comfyui_prep03_smoke_api.json`, `docs/TEST_RESULTS.md` |
| **PREP-04** | Autorig и skinning: нативные auto weights + rigid attachment; сравнение UniRig/MeshRig и др. | `PLANNED` | частично: auto weights проверены на манекене (PREP-01) |
| **PREP-05** | Новые анимации: реальный bone clip из Blender/Cascadeur; локальные AI motion кандидаты | `PLANNED` | — |
| **PREP-06** | Оркестрация и контракты без кастомизации: manifest/schema, команды-образцы, решение Python vs n8n | `PLANNED` | — |
| **PREP-07** | Интеграционная демонстрация: модель → rig → skinning → клип → воспроизводимость | `PLANNED` | — |
| **ORC-01** | Технический прототип модульной voxel-модели: генерация → Blender 5.2.4 → `.blend` → GLB round-trip → 3 вида | **READY_FOR_REVIEW** (технический PASS; визуально не утверждено) | `docs/prototypes/ORC01_LOCAL_VALIDATION.md`, `outputs/prototypes/orc_01/`, `logs/ORC-01_*`, `scripts/voxel/*`, `scripts/blender/orc01_*` |

Разрыв между «инструмент есть» и «конвейер работает» фиксируется в `docs/PIPELINE_GAPS.md`.

## 6. Инвентарь кандидатов (не означает установки)

| Инструмент | Задача | Факт установки (2026-11-13) | Следующее действие |
|---|---|---|---|
| **Blender** | mesh, armature, skinning, animation export, CLI | **5.2.4 LTS** — `D:\programs\Blender\5.2\blender.exe`; SHA-256 сверен; GUI/headless/Rigify/skinning/FBX проверены | PREP-02: обмен форматами |
| Rigify | metarig → control rig | **0.6.10** встроенный; rig 706 костей (160 DEF); auto weights + позы проверены | PREP-04: сравнить с autorig-кандидатами |
| Python + venv | smoke runner, среды | **3.13.14** в PATH; `venv` работает | `environments\venv-prep` **не создавался осознанно** — Blender несёт свой Python 3.13.13, внешний runner появится на PREP-02 |
| **ComfyUI** | AI-workflows | **0.45.0 portable** — `D:\programs\ComfyUI\`; сервер/UI/API smoke PASS; CUDA работает | Согласовать конкретную AI-модель (источник/размер/лицензия/VRAM) → тест генерации |
| 7-Zip CLI | распаковка `.7z` | **7zr.exe 26.04** в `D:\programs\_installers\` (public domain, PATH не менялся) | — |
| Cascadeur | авторинг motion, FBX | **NOT_INSTALLED** | Сначала лицензия/тариф/экспорт FBX — потом решение |
| Локальная 3D AI | новое 3D / переработка mesh | NOT_SELECTED | Сравнить кандидатов и VRAM (≤6.7 ГБ фактически) |
| Autorig/skin tool | skeleton fitting, auto weights | NOT_SELECTED | PREP-04: кандидаты + лицензии + evidence |
| Локальная Motion AI | черновые скелетные анимации | NOT_SELECTED | PREP-05: проверить скелетный выход на 8 ГБ |
| n8n | очереди и ошибки | **NOT_INSTALLED**; системного Node.js нет | Не ставить без доказанного преимущества |
| **Unity** | конечный consumer | **6000.3.27f2** и 6000.6.7f1, Hub 3.22.5 | Только обнаружение; CubeGame не открывать |
| Git | версии/отчёты | **2.55.0**; локальный репозиторий создан, identity задана локально | Добавить remote после получения URL |
| VS Code | редактор | **1.145.2** | — |
| Ollama | локальная LLM | **0.40.10**, не запущен | Не требуется на PREP-00/01 |

Инвентарь с путями и статусами — `docs/TOOL_INVENTORY.md`.

## 7. Проблемы, риски и открытые вопросы

**Подтверждённые блокеры (PREP-00):**
- **B1 — Blender отсутствует.** **ЗАКРЫТ 2026-11-13 (PREP-01):** установлен Blender 5.2.4 LTS, все базовые операции проверены.
- **B2 — ComfyUI не найден.** **ЗАКРЫТ 2026-11-13 (PREP-03):** установлен официальный portable 0.45.0, runtime/API проверены. Остаётся прикладной вопрос (не блокер): какие AI-модели использовать и сколько они займут VRAM.
- **B3 — remote Factory-репозитория не было.** **ЗАКРЫТ 2026-11-13:** `origin` = `alfuwerce-art/factoria.git`, `factory/work` синхронизирована и проверена.
- **B4 — Git identity была не настроена** (`user.name`/`user.email` пусты). **ЗАКРЫТ 2026-11-13:** identity задана локально в репозитории (`DeepSeek Harness`, `factory-lab@localhost`); global-настройки не менялись.

**Ловушки, выявленные практикой (не повторять):**
- `addon_utils.enable("rigify")` в 5.2.4 **непригоден**: генерация падает с `'RigifyParameters' object has no attribute 'make_custom_pivot'`. Работает `bpy.ops.preferences.addon_enable(module='rigify')`.
- Bone Heat Weighting **полностью отказывает** на несвязной геометрии (160 боксов → 0 весов). Сначала voxel remesh в одну оболочку, потом auto weights.
- Rigify DEF-кости **не** управляются напрямую (constraints): позы только через control-кости (`*_ik`, `*_fk` при `IK_FK=1.0`).
- Auto weights **не нормирует** веса (0.73–0.9999) → нужен шаг нормализации (PIPELINE_GAPS F8).
- FBX выгружает весь control rig (706 костей) — нужен отдельный deform-only экспорт (F9).
- ComfyUI **первый запуск ~146 с** (SQLite-миграция + скан ассетов): readiness-timeout в оркестраторе ≥300 с (F13).
- **PowerShell 5.1:** `.ps1` с кириллицей сохранять **в UTF-8 с BOM**, иначе парсер ломается; `Start-Process -ArgumentList` не квотирует пути с пробелами — оборачивать аргументы в кавычки самому.
- `nvidia-smi --query-compute-apps` на Windows/WDDM не показывает память процесса ComfyUI (возвращает 0) — VRAM мерить по всей карте и вычитать baseline.

**Известные риски:**
- 8 ГБ VRAM ограничивают локальные 3D / motion модели;
- image-to-3D не равен контролируемой переработке существующей 3D-геометрии;
- auto skinning может ломать плечи/таз/броню; для жёстких кубических частей может быть достаточно bone parenting;
- Rigify не является автоматическим классификатором анатомии и universal rig fitter;
- внешние лицензии и платные экспорты могут ограничивать использование;
- независимый smoke test не доказывает совместимость с реальным Unity Player.

**Решения ожидают подтверждения:** выбор конкретной AI-модели/кандидатов (источник, размер, лицензия, VRAM), установка Cascadeur (после лицензии), нужен ли n8n, какие части Python automation понадобятся позже.

**Открытые вопросы к пользователю (минимально необходимое):**
1. **ORC-02:** визуальная оценка прототипа (`MODEL_APPROVED`/`MODEL_REWORK`) и решение — предоставить легальную рабочую копию существующего Orc или доводить новую процедурную модель.
2. Согласование AI-модели для ComfyUI (источник, размер, лицензия, требуемая VRAM, качество) — только после этого тест генерации/переработки геометрии.
3. Cascadeur: лицензия/тариф и ограничения экспорта FBX (перед установкой).
4. Приёмка (ACCEPTED) по PREP-00/PREP-01/ORC-01 — сейчас все `READY_FOR_REVIEW`.

## 8. Хронология работ (append-only, кратко)

| Дата | Этап | Что сделано | Где доказательства | Следующее действие |
|---|---|---|---|---|
| 2026-11-13 | Подготовка ТЗ и памяти | Созданы три стартовых документа; установки и тесты не запускались в рамках данной подготовки | Документы 01–03 | PREP-00: обнаружение существующего ПО и среды |
| 2026-11-13 | PREP-00 (сессия 1) | Прочитаны все 4 документа. Обнаружено, что `D:\Projects\CubeGameFactoryLab` отсутствует, а документы лежат в `D:\Projects\CubeGame Factory`. Создан канонический каталог + структура ТЗ §4, 4 документа скопированы с совпадением SHA-256 | sha256-сравнение в выводе сессии; `D:\Projects\CubeGameFactoryLab` | Аудит железа |
| 2026-11-13 | PREP-00 (сессия 1) | Выполнен аудит: OS/CPU/RAM/GPU/диски, 92 записи Uninstall, PATH-пробы, рекурсивный поиск Blender/Cascadeur/ComfyUI, порты, процессы. Подтверждено железо из ТЗ, VRAM 8188 MiB. **Blender/ComfyUI/Cascadeur/n8n отсутствуют** | `logs/PREP-00_detection_2026-11-13.txt` (177 строк, UTF-8) | Написать журналы |
| 2026-11-13 | PREP-00 (сессия 1) | Созданы `docs/TOOL_INVENTORY.md`, `docs/INSTALLATION_LOG.md`, `docs/LICENSE_MATRIX.md`, `docs/TEST_RESULTS.md`, `docs/PIPELINE_GAPS.md`, `README.md`. Лицензия Blender (GPL-2.0-or-later) и сборка 5.2.4 LTS подтверждены по официальному зеркалу | `docs\*`, `logs\*` | PREP-01: установка Blender |
| 2026-11-13 | Консолидация каталога | Рабочая папка сведена к `D:\Projects\CubeGame Factory`: перенесены журналы, доказательства и git-история из `CubeGameFactoryLab`; путь в AGENTS.md исправлен (3 вхождения); устаревшая память v1.1 перемещена в `docs\archive\` | `git log`, `docs\archive\` | Настроить режим |
| 2026-11-13 | Режим DSH | Создан и установлен пользовательский пресет `cubegame-factory` (CubeGame Factory) на базе Standard: persona с рабочей директорией, четырьмя документами, RAM-first и правилами отчётности. Строка активна, встроенные режимы не изменены | `plugins\cubegame-factory-preset\`; `C:\Users\bow\.dsh\profiles\desktop\package.json` | Открыть новый чат в этом режиме |
| 2026-11-13 | PREP-01 (установка) | Скачан `blender-5.2.4-windows-x64.zip` (405 779 142 Б) + `.sha256` с `download.blender.org`; SHA-256 сверен (`bbd78f89…967c`), распакован `tar` в `D:\programs\Blender\5.2\` (901.3 МБ). PATH не менялся, конфиг изолирован в `environments\blender\config` | `logs\PREP-01_isolation_2026-11-13.txt`; `docs\INSTALLATION_LOG.md` | Проверить запуск |
| 2026-11-13 | PREP-01 (smoke) | Headless `--background` PASS: версия 5.2.4 LTS, Python 3.13.13, создание/сохранение `.blend` (86 КБ). GUI PASS: открыт `prep01_rigify_skinned.blend`, заголовок окна подтверждает файл, скриншот сохранён | `logs\PREP-01_headless_smoke_2026-11-13.txt`; `outputs\blender\prep01_gui_open.png` | Rigify |
| 2026-11-13 | PREP-01 (отладка) | Найдены и зафиксированы 3 реальные ловушки: `addon_utils.enable('rigify')` ломает генерацию; heat weighting отказывает на несвязных боксах (0 весов); DEF-кости Rigify не управляются напрямую. Исправлено: официальный `addon_enable`, voxel remesh в одну оболочку, позы через control-кости | `logs\PREP-01_diagnostics_2026-11-13.txt` | Полный прогон |
| 2026-11-13 | PREP-01 (результат) | Полный прогон PASS: rigify_generate (159→706 костей), auto weights (160 групп, 0 вершин без весов), деформация IK 0.562 м / FK 0.332 м, рендеры rest+posed различаются, `.blend` 574 КБ, FBX 1.54 МБ и обратный импорт с рабочей деформацией 0.566 м. Прогон 11.8–12.0 с, пик 394–402 МБ RAM, CPU-рендер (VRAM не занималась) | `logs\PREP-01_rigify_skinning_2026-11-13.txt`; `outputs\reports\prep01_rigify_skinning.json`; `outputs\blender\prep01_rigify_skinned.blend/.fbx`; PNG | PREP-02 |
| 2026-11-13 | PREP-01 (документация) | Обновлены `docs\TEST_RESULTS.md` (PREP-01 yaml + измерения + ловушки), `docs\TOOL_INVENTORY.md`, `docs\INSTALLATION_LOG.md`, `docs\LICENSE_MATRIX.md`, `docs\PIPELINE_GAPS.md` (G1 закрыт, добавлены F8–F10), `README.md` | `docs\*`, `README.md` | Коммит в `factory/work` |
| 2026-11-13 | GitHub-миграция | Добавлен remote Factoria; `fetch` показал несвязанные истории; `merge --allow-unrelated-histories` (конфликт только `README.md`, взят локальный + раздел о маршрутизации) → merge-коммит `8395409`; push `ca5bfef..8395409`; проверено `HEAD == origin/factory/work`, `diff` пустой, 47 файлов на remote | `docs\MIGRATION_STATUS.md`; `git log --graph` | Четыре документа, скрипты, PREP-00/01 и доказательства опубликованы |
| 2026-11-13 | PREP-03 (установка) | Скачан и проверен официальный ComfyUI 0.45.0 portable NVIDIA (1.93 ГБ, SHA-256 совпал), распакован `7zr.exe` в `D:\programs\ComfyUI\` (4.25 ГБ); embedded python 3.13.14 + torch 2.14.1+cu130; PATH и системный Python не менялись | `logs\PREP-03_cuda_sanity_2026-11-13.txt`; `docs\INSTALLATION_LOG.md` | Запуск и API smoke |
| 2026-11-13 | PREP-03 (испытание) | GPU (`--reserve-vram 5`) и CPU (`--cpu`) прогоны PASS: сервер 10.7–11.8 с (холодный ~146 с), UI 200, `POST /prompt` → `/history` → `/view`, PNG 96×96; пик RAM процесса 972/859 МБ, прирост VRAM ≈86 МБ; CUDA matmul 0.12 с, allocated 56.1 МБ | `logs\PREP-03_run_gpu/cpu_2026-11-13.txt`; `outputs\reports\prep03_comfyui_smoke_*.json`; `outputs\comfyui\prep03_smoke_from_api.png` | Документация + commit/push |
| 2026-11-13 | PREP-03 (документация) | Обновлены `TEST_RESULTS` (PREP-03 yaml + карточка RAM/VRAM), `TOOL_INVENTORY`, `INSTALLATION_LOG`, `LICENSE_MATRIX` (ComfyUI GPL-3.0, torch/CUDA, 7zr), `PIPELINE_GAPS` (G2 закрыт, F11–F13), `MIGRATION_STATUS` (ComfyUI-раздел), `README`, память v1.5 | `docs\*`, `README.md`, `03_FACTORY_PROJECT_MEMORY.md` | Коммит в `factory/work` |
| 2026-11-13 | ORC-01 (перенос) | `git merge --ff-only` до remote `909bc94` (документы FACT-D17 и ORC-пилот). Найден и распакован архив `FACTORIA_ORC_01_package.zip` (78 966 Б); генератор и превью-скрипт перенесены в `scripts/voxel/`, handoff-артефакты — в `outputs/prototypes/orc_01/handoff/` | `outputs\prototypes\orc_01\handoff\*`, `logs\ORC-01_generator_2026-11-13.txt` | Локальная генерация |
| 2026-11-13 | ORC-01 (генерация) | Локальный прогон: 0.18 с, 12.9 МБ RAM, 211 боксов/20 модулей/2532 треугольника; два прогона идентичны; исходный генератор воспроизвёл handoff-GLB байт-в-байт; seed 23 отличается | `outputs\prototypes\orc_01\generated\*`, `logs\ORC-01_glb_inspect_2026-11-13.txt` | Проверка GLB инспектором |
| 2026-11-13 | ORC-01 (дефекты) | Найдены 2 дефекта: пересечение 4 стыков конечностей; `COLOR_0` без `normalized` (Blender показывал белый). Исправлены минимальной правкой генератора; после правок 0 issues, зазоры 0.020–0.045 м | `scripts\voxel\orc_prototype.py`; `outputs\prototypes\orc_01\reports\glb_inspect_*.json` | Blender-проверка |
| 2026-11-13 | ORC-01 (Blender) | Импорт 20 модулей, целостность, материалы/цвета, оси/масштаб, независимое редактирование, зазоры, `.blend` сохранён и переоткрыт, GLB round-trip без потерь, 3 вида (Cycles CPU). Пик RAM 281–315 МБ, VRAM не использовалась | `logs\ORC-01_blender_2026-11-13.txt`, `logs\ORC-01_blend_reopen_2026-11-13.txt`, `outputs\prototypes\orc_01\blender\*`, `outputs\prototypes\orc_01\reports\blender_roundtrip.json` | Документация + commit/push |
| 2026-11-13 | ORC-01 (документация) | Создан `docs\prototypes\ORC01_LOCAL_VALIDATION.md`; обновлён статус пилота; добавлено исключение в `.gitignore` для `outputs/prototypes/**/*.glb`; память v1.6 | `docs\prototypes\*`, `.gitignore`, `03_FACTORY_PROJECT_MEMORY.md` | Commit/push |

## 9. Что делать DeepSeek прямо в следующем чате

**Выполнено в PREP-00 (2026-11-13):** пп. 1–4 ниже закрыты — документы прочитаны, каталог создан, аудит проведён, журналы написаны.

**Выполнено в PREP-01 (2026-11-13):** Blender 5.2.4 LTS установлен и проверен; Rigify сгенерировал rig; auto weights, контрольные позы, FBX-экспорт и обратный импорт доказаны на собственной фигуре. Статус `READY_FOR_REVIEW`.

**Выполнено в PREP-03 (2026-11-13, частично):** ComfyUI 0.45.0 portable установлен и проверен как runtime: сервер, UI, API-workflow без моделей, CUDA-вычисления встроенного torch, замеры RAM/VRAM. Статус `PARTIAL` — AI-модели и генерация 3D не проверялись.

**Выполнено в ORC-01 (2026-11-13):** перенесённый генератор отработал локально; GLB проверен независимым stdlib-инспектором; найдены и минимально исправлены 2 дефекта (пересечение 4 стыков конечностей, `COLOR_0` без `normalized`); модель импортирована в Blender 5.2.4 (20 независимых модулей), `.blend` сохранён и переоткрыт, GLB round-trip без потерь, отрендерены 3 вида. Статус `READY_FOR_REVIEW`; **визуальной приёмки нет** (`MODEL_PENDING_REVIEW` по FACT-D17).

**Следующая сессия — выбор владельца:**

1. **ORC-02 — художественная детализация:** нужна либо легальная редактируемая рабочая копия существующего Orc (её нет — есть только PNG-референсы), либо явное решение доводить новую процедурную модель. После этого — визуальная приёмка `MODEL_APPROVED`/`MODEL_REWORK` (FACT-D17).
2. **PREP-02 (форматы/экспорт)** — плановый этап PREP, не отменён: `.blend`/`.fbx`/`.glb` round-trip с осями, материалами и action; deform-only скелет вместо 706-костного Rigify control rig.
3. Проверить перед работой: `git -C "D:\Projects\CubeGame Factory" pull --ff-only`, `Test-Path D:\programs\Blender\5.2\blender.exe`, `Test-Path outputs\prototypes\orc_01\blender\orc01_modular.blend`, `Test-Path D:\programs\ComfyUI\run_nvidia_gpu.bat`.
4. **Не делать** без отдельного разрешения: риг/анимации/эмоции на прототипе, установка AI-весов, массовая генерация, любые действия в CubeGame/Unity.

## 10. Протокол обновления межчатовой памяти

При завершении каждого блока работы исполнитель обязан:

- поменять статус только у фактически выполненных задач; явно различать `INSTALLED`, `SMOKE_PASS`, `PARTIAL`, `BLOCKED`;
- записать точный инструмент, версию, путь, источник, лицензию, проверенную команду и выходные артефакты в соответствующие журналы;
- добавить одну строку в хронологию, обновить следующий шаг и незакрытые проблемы;
- не удалять старые результаты — отмечать их как `SUPERSEDED`, если выяснилась ошибка;
- не менять утверждённые решения по собственному усмотрению;
- не заявлять готовность Factory по smoke tests отдельных программ;
- если пользователь принял результат, записать дату и формулировку приёмки; иначе оставить `READY_FOR_REVIEW`.

**Состояние на создание файла:** PREP не выполнялся; все три документа являются спецификацией и начальной памятью. Реальные установленные компоненты DeepSeek установит по проверке, а не по предположениям.
