# COMFY-STYLE-04 — RUN REPORT (DreamShaper XL + Pixel-Textured 3D)

**Дата:** 2026-11-13 · **Ветка:** `factory/work` · **Репозиторий:** `alfuwerce-art/factoria`
**Основание:** AUTHORIZED_FOR_SETUP, решение `FACT-D20` (экспериментальный стиль)
**Статус:** `PARTIAL` — подготовка выполнена, веса докачиваются (см. §7), реальные пики RAM/VRAM
не измерены: на момент работ на машине работали ComfyUI владельца и Unity.

---

## 1. Сводка

```text
TASK=COMFY-STYLE-04
STATUS=PARTIAL

COMFY_PATH=D:\programs\ComfyUI (существующая установка, вторая не создавалась)
COMFY_VERSION=0.45.0
FACTORIA_LAB=D:\Projects\CubeGame Factory   (рабочая папка лаборатории/репозитория)
CUBEGAME_PROJECT=D:\Projects\CubeGame       (игровой проект; НЕ изменялся)
PYTHON=3.13.14 embedded | TORCH=2.14.1+cu130 | CUDA=13.0 | GPU RTX 4060 Laptop 8188 MiB

CHECKPOINT=DreamShaperXL_Turbo_v2_1.safetensors (Lykon/dreamshaper-xl-v2-turbo, openrail++)
CHECKPOINT_SIZE=6 939 220 250 B
CHECKPOINT_SHA256=4496b36d48bfd7cfe4e5dbce3485db567bcefa2bef7238d290dbd45612125083
SD15_BACKUP=v1-5-pruned-emaonly-fp16.safetensors — сохранён, не изменялся

STYLE_MODULE=VoxelXL_v1.safetensors (Fictiverse/Voxel_XL_Lora, openrail, trigger "voxel style")
IPADAPTER=ip-adapter-plus_sdxl_vit-h.safetensors (apache-2.0) + CLIP-ViT-H-14 (2.53 GB)
CONTROLNET=controlnet-union-sdxl-1.0.safetensors (xinsir, apache-2.0)

LAUNCHER_DEFAULT=scripts\comfyui\launch_dreamshaper_xl.bat        (--reserve-vram 1)
LAUNCHER_RAM_FIRST=scripts\comfyui\launch_dreamshaper_xl_novram.bat (--novram --reserve-vram 5)
LAUNCHER_CPU=scripts\comfyui\launch_cpu_fallback.bat              (--cpu)

WORKFLOWS=workflows\dreamshaper_xl\{DREAMSHAPER_XL_BASE,DREAMSHAPER_XL_PIXEL_STYLE,
          DREAMSHAPER_XL_REFERENCE_LOCK,DREAMSHAPER_XL_POSE_CONTROL}.json
PROMPTS=workflows\dreamshaper_xl\prompt_orc_v1.json (§first_test)

GIT_BRANCH=factory/work
```

## 2. Фактическая среда (проверено)

| Пункт | Факт |
|---|---|
| ComfyUI | `D:\programs\ComfyUI`, 0.45.0, portable, `python_embeded` 3.13.14, torch 2.14.1+cu130 |
| Рабочая папка Factoria | `D:\Projects\CubeGame Factory` — репозиторий лаборатории (`factory/work`) |
| Игровой проект CubeGame | `D:\Projects\CubeGame` — существует, **не открывался и не изменялся** (только `git status`, read-only) |
| Вторая установка ComfyUI | не создавалась |
| SD 1.5 | сохранён как резервный (`v1-5-pruned-emaonly-fp16.safetensors`, 2.03 ГБ) |
| Существующие workflow | не изменялись (`workflows/factoria_voxel_style/*` на месте) |
| Загрузка во время работ | сервер владельца на порту 8188 (pid 24988, `--novram --reserve-vram 5`) + Unity занимали RAM/GPU — поэтому тяжёлые прогоны не запускались |

## 3. Выбор моделей (обоснование — `docs/decisions/FACT-D20-dreamshaper-xl-experimental-style.md`)

| Роль | Файл | Лицензия | Размер | SHA-256 |
|---|---|---|---|---|
| Checkpoint | `DreamShaperXL_Turbo_v2_1.safetensors` | openrail++ | 6 939 220 250 B | `4496b36d…5083` |
| LoRA | `VoxelXL_v1.safetensors` | openrail | 912 554 516 B | `7d9a5f11…8b5c` |
| IPAdapter | `ip-adapter-plus_sdxl_vit-h.safetensors` | apache-2.0 | 847 517 512 B | `3f5062b8…6581` |
| CLIP Vision | `CLIP-ViT-H-14-laion2B-s32B-b79K.safetensors` | open_clip/MIT, веса LAION-2B | 2 528 373 448 B | `6ca9667d…b030` |
| ControlNet | `controlnet-union-sdxl-1.0.safetensors` | apache-2.0 | 2 512 030 408 B | `a9e13fd6…7467` |

Отклонено и почему:
- `nerijs/pixel-art-xl` — 2D pixel art, прямо противоречит требованию «объёмный 3D-персонаж»;
- одиночный single-file DreamShaper XL 1.0 — только Civitai (нужен аккаунт/токен; не используется),
  на HF `Lykon/dreamshaper-xl-1-0` есть лишь diffusers-раскладка;
- 3 отдельных SDXL ControlNet (canny + lineart + openpose ≈ 7.5 ГБ) — заменены одним union-файлом;
- `ip-adapter_sdxl` (ViT-bigG 3.69 ГБ) — дороже по VRAM без выигрыша для нашей задачи;
- `ntc-ai/SDXL-LoRA-slider.voxels` (8.8 МБ) — оставлен как дешёвая альтернатива, не скачивался.

## 4. Workflow

Все четыре собраны **программно** из `prompt_orc_v1.json` и живого `/api/object_info`
(`scripts/comfyui/build_dreamshaper_xl_workflows.py`), затем проверены структурно
(`measurements/dreamshaper_xl_build_report.json`).

| Workflow | Ноды / связи | Что внутри | Статус |
|---|---|---|---|
| `DREAMSHAPER_XL_BASE.json` | 8 / 9 | SDXL txt2img 768×1024 batch 1, 8 шагов, CFG 2.0, fixed seed, SaveImage `factoria/xl_base` | собран, структурно PASS |
| `DREAMSHAPER_XL_PIXEL_STYLE.json` | 9 / 11 | + `LoraLoader` VoxelXL (weight 1.0), триггер `voxel style` первым в промпте | собран, структурно PASS |
| `DREAMSHAPER_XL_REFERENCE_LOCK.json` | 11 / 13 | + `LoadImage` → `IPAdapterUnifiedLoader` → `IPAdapterAdvanced` (weight 0.7, `style transfer`) | собран, структурно PASS |
| `DREAMSHAPER_XL_POSE_CONTROL.json` | 14 / 16 | + ControlNet-ветка: LoadImage → Canny/Lineart/DW-Pose (MUTE) → ControlNetLoader (MUTE) → ControlNetApplyAdvanced (**BYPASS**) | собран, структурно PASS |

Принципы, чтобы не было «незаметно неправильной ветки»:
- LoRA/IPAdapter-ноды **не** замаскированы: нет весов → явная ошибка при Queue, тихого отката нет;
- ControlNet-ветка выключена видимо (BYPASS + MUTE) и включается владельцем осознанно;
- промпты лежат в контракте и продублированы в нодах; первый Orc-тест — отдельные ноды
  `POSITIVE - first Orc test` / `NEGATIVE`.

## 5. Запуск

```bat
D:\Projects\CubeGame Factory\scripts\comfyui\launch_dreamshaper_xl.bat        :: --reserve-vram 1
D:\Projects\CubeGame Factory\scripts\comfyui\launch_dreamshaper_xl_novram.bat :: RAM-first
D:\Projects\CubeGame Factory\scripts\comfyui\launch_cpu_fallback.bat         :: --cpu
```

`--novram --reserve-vram 5` (режим SD1.5) для SDXL проверен как **нежелательный по умолчанию**:
он оставляет карте ~3 ГБ при ~6.9 ГБ весов SDXL. Поэтому для SDXL сделан отдельный launcher с
`--reserve-vram 1` (~7 ГБ карты). Оба варианта оставлены, чтобы владелец мог сравнить на практике.
`--lowvram/--highvram/--gpu-only/--cpu/--novram` — одна взаимоисключающая группа, вместе не подаются.

## 6. Технические проверки

| Проверка | Результат |
|---|---|
| Целостность весов (SHA-256) | см. §7 — статус на момент отчёта |
| Структурная сборка 4 workflow против `/api/object_info` | **PASS** |
| Регистрация нод (LoRA, IPAdapter, ControlNet, препроцессоры) | **PASS** (в `/object_info` 1213 типов, все нужные присутствуют) |
| Ошибки импорта custom nodes | **нет** (проверено ранее в COMFY-STYLE-02/03, состояние не менялось) |
| Прежние workflow / SD 1.5 | не изменялись |
| Загрузка SDXL через torch/CUDA | ожидает завершения загрузки чекпоинта |
| Реальный прогон и пики RAM/VRAM | **NOT_TESTED** — на машине работали ComfyUI владельца и Unity |

## 7. Состояние загрузок

| Файл | Статус |
|---|---|
| DreamShaper XL Turbo v2.1 | качается (`scripts\comfyui\fetch_style04_models.ps1`, лог `logs\COMFY-STYLE-04_download_2026-11-13.log`) |
| CLIP ViT-H-14 | в очереди |
| ip-adapter-plus_sdxl_vit-h | в очереди |
| controlnet-union-sdxl-1.0 | в очереди |
| VoxelXL_v1 (LoRA) | в очереди |

Скорость HF на этой машине: 0.4–1.0 МБ/с даже при 12 параллельных диапазонах (одиночный поток
падает до 20–60 КБ/с). Полный набор ≈13.7 ГБ, поэтому загрузка идёт фоном и **возобновляема**:

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File `
  "D:\Projects\CubeGame Factory\scripts\comfyui\fetch_style04_models.ps1" -Connections 12
```

Скрипт идемпотентен: уже скачанные файлы проверяются по SHA-256 и не перекачиваются.

## 8. Что осталось (следующий шаг)

1. Дождаться завершения `fetch_style04_models.ps1` (или запустить его повторно — продолжит с места).
2. Проверить загрузку чекпоинта без генерации:
   `python_embeded\python.exe -s scripts\comfyui\load_checkpoint_probe.py` (с `FACTORIA_CKPT`).
3. Технический прогон графа (не художественная оценка) и замер пиков:
   `scripts\comfyui\xl_run_workflow.py --workflow workflows\dreamshaper_xl\DREAMSHAPER_XL_BASE.json ...`.
4. Владелец: открыть `DREAMSHAPER_XL_PIXEL_STYLE.json`, Queue, оценить персонажа.

## 9. Известные ограничения

- Turbo-модель: 6–10 шагов и CFG 1.5–2.5; тонкая детализация слабее, чем у классического DSXL.
- LoRA `VoxelXL` может давать «игрушечный» воксельный вид; альтернатива — `REFERENCE_LOCK`.
- SDXL на 8 ГБ VRAM с большой вероятностью превысит лимит «+2 ГБ VRAM» — это будет измерено и
  зафиксировано честно; лимит не «подкручивается».
- IPAdapter/ControlNet требуют ещё ~5.9 ГБ весов на диске (место есть: 630 ГБ свободно).
