# DREAMSHAPER XL — Pixel-Textured 3D (COMFY-STYLE-04)

Экспериментальный стилевой стек: **SDXL DreamShaper XL Turbo v2.1** + **VoxelXL LoRA** /
**SDXL IPAdapter** / **SDXL union ControlNet**. Стиль **не утверждён** — приёмка только
владельцем после первой генерации персонажа.

## Файлы

| Workflow | Что делает | Нужны веса |
|---|---|---|
| `DREAMSHAPER_XL_BASE.json` | SDXL txt2img 768×1024, batch 1, без стилевых модулей | `DreamShaperXL_Turbo_v2_1.safetensors` |
| `DREAMSHAPER_XL_PIXEL_STYLE.json` | + LoRA `VoxelXL_v1.safetensors` (триггер **voxel style**) | + LoRA |
| `DREAMSHAPER_XL_REFERENCE_LOCK.json` | + SDXL IPAdapter по локальному референсу | + `ip-adapter-plus_sdxl_vit-h` + CLIP ViT-H + референс в `input/` |
| `DREAMSHAPER_XL_POSE_CONTROL.json` | + отключаемая ветка ControlNet (union: canny / lineart / dwpose) | + `controlnet-union-sdxl-1.0` |
| `DREAMSHAPER_XL_CIVITAI_VOXEL.json` | **орк**, Civitai LoRA `ral-vxl` (trigger `ral-vxl`, strength 0.6) | + `ral-vxl.safetensors` |
| `DREAMSHAPER_XL_CIVITAI_VOXEL_HUMAN.json` / `..._ELF.json` | сравнительные тесты рас (тот же стиль-блок, меняется только раса) | + `ral-vxl.safetensors` |
| `prompt_orc_v1.json` | контракт: positive/negative под первый Orc-тест, настройки, лимиты | — |
| `prompt_voxel_face_lock_v1.json` | BODY_STYLE_LOCK + FACE_STYLE_LOCK, расовые блоки, negative, сравнительный тест | — |

### Civitai «Voxel Style [SDXL]» — важное ограничение

Файл `ral-vxl.safetensors` (Civitai 461862, автор RalFinger) установлен **только для эксперимента**:
`allowCommercialUse=RentCivit`, `allowDerivatives=False`, `allowNoCredit=False` — коммерческое
использование изображений автором не разрешено, производные запрещены. Поэтому:
- основная стилевая LoRA остаётся **Fictiverse Voxel XL** (openrail);
- результаты на `ral-vxl` нельзя переносить в релиз без письменного разрешения автора;
- производственная альтернатива — SDXL IPAdapter по собственному референсу или собственная
  `Factoria Style LoRA` на собственных/лицензированных изображениях.
Подробнее: `docs/decisions/FACT-D21-civitai-voxel-lora-license.md`.

### Voxel Face Style Lock

`BODY_STYLE_LOCK` и `FACE_STYLE_LOCK` — это **два блока одного промпта**, а не независимое
управление стилями (пока архитектурное требование). Сравнительный тест: орк → человек → эльф на
одном seed и одной силе LoRA; критерий — единый воксельный язык, читаемые расовые особенности,
взрослые пропорции лица, разделённые конечности, полный рост.

## Запуск

```bat
D:\Projects\CubeGame Factory\scripts\comfyui\launch_dreamshaper_xl.bat
```

`--reserve-vram 1` (динамическая VRAM, ~7 ГБ карты под ComfyUI). Если пойдёт в shared memory
или начнёт постоянно выгружать/загружать веса — RAM-first вариант:

```bat
D:\Projects\CubeGame Factory\scripts\comfyui\launch_dreamshaper_xl_novram.bat
```

Крайний случай — `launch_cpu_fallback.bat` (`--cpu`, без GPU-инференса).
Нельзя совмещать `--novram/--lowvram/--highvram/--gpu-only/--cpu` — это одна
взаимоисключающая группа аргументов.

UI: <http://127.0.0.1:8188> → `Workflow → Open` → нужный `DREAMSHAPER_XL_*.json`.

## Настройки turbo (важно)

DreamShaper XL Turbo — дистиллированная модель: **6–10 шагов, CFG 1.5–2.5** (в workflow 8 / 2.0).
Классический (не turbo) DS XL потребовал бы 25–30 шагов и CFG 7 — если владелец решит
перейти на него, шаги/CFG меняются в ноде `KSampler`.

Разрешения: 768×1024 (по умолчанию), 768×768 (быстрее), 1024×1024 — только после замера памяти.

## Первый Orc-тест

1. Открыть `DREAMSHAPER_XL_BASE.json` (проверка базовой модели) или сразу
   `DREAMSHAPER_XL_PIXEL_STYLE.json` (стиль LoRA).
2. Промпты уже вписаны в ноды **POSITIVE - first Orc test** / **NEGATIVE**
   (источник — `prompt_orc_v1.json`, §first_test).
3. **Queue**. Результат: `ComfyUI/output/factoria/xl_*.png`.
4. Записать пик RAM/VRAM из панели **Crystools** и время генерации.

## Чего эти workflow не делают

- не запускают Tripo, Blender, rig, animation, Unity;
- не подтверждают стиль: стиль считается экспериментальным до решения владельца;
- не подменяют отсутствующие веса тихим откатом: если LoRA/IPAdapter/ControlNet не установлены,
  соответствующая нода даёт явную ошибку при Queue (ветка ControlNet по умолчанию в BYPASS/MUTE —
  это единственное исключение, и оно видно в UI).
