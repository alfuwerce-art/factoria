# FACTORIA VOXEL_STYLE — готовые workflow ComfyUI

Этап COMFY-STYLE-02/03 (решение FACT-D19). Здесь лежит «инструмент», а не инфраструктура:
открыл → выбрал reference → ввёл персонажа → Queue.

| Файл | Что делает | Нужны веса |
|---|---|---|
| `FACTORIA_VOXEL_STYLE_BASE.json` | базовая генерация SD1.5, без IPAdapter и ControlNet | только checkpoint `v1-5-pruned-emaonly-fp16.safetensors` |
| `FACTORIA_VOXEL_STYLE_IPADAPTER.json` | style reference (voxel-язык) через IPAdapter | + CLIP Vision + `ip-adapter-plus_sd15` |
| `FACTORIA_VOXEL_STYLE_CONTROL_TEMPLATE.json` | то же + отключаемая ветка ControlNet | + веса ControlNet (ветка в BYPASS) |
| `voxel_style_prompt_v1.json` | контракт стиля: префикс, блок персонажа, negative | — |

## Запуск

```bat
D:\Projects\CubeGame Factory\scripts\comfyui\launch_safe_baseline.bat
```

Открыть <http://127.0.0.1:8188> → `Workflow → Open` → выбрать нужный `FACTORIA_*.json`
(или перетащить файл в окно).

Если `--novram` выходит за лимит по памяти — второй режим:

```bat
D:\Projects\CubeGame Factory\scripts\comfyui\launch_cpu_fallback.bat
```

Ресурсы: панель **Crystools** в верхней строке UI (RAM / VRAM / CPU / GPU, время хода).
Лимиты этапа: RAM ≤ 15 GB, дополнительная VRAM ≤ 2 GB сверх baseline до запуска.

## Первый прогон (базовый, без весов IPAdapter)

1. Открыть `FACTORIA_VOXEL_STYLE_BASE.json`.
2. В ноде **POSITIVE - style + character** заменить только блок после `|`
   (раса, пол, телосложение, лицо, одежда, броня, аксессуары, палитра, поза, камера).
   Стилевой префикс не менять — он и есть фиксация стиля.
3. **Queue**. Результат: `ComfyUI/output/factoria/voxel_style_base_*.png`.

## Style reference (Orc)

Локальный reference-файл владельца **не публикуется** и не вшит в workflow:

1. Скопировать изображение в `D:\programs\ComfyUI\ComfyUI\input\` под именем
   `factoria_style_reference.png` (или выбрать своё имя в ноде LoadImage).
2. Открыть `FACTORIA_VOXEL_STYLE_IPADAPTER.json`, выбрать файл в ноде **LoadImage**.
3. Первый запуск потребует весов (список с размерами/хэшами — в
   `docs/tasks/COMFY-STYLE-02_03_RUN_REPORT.md`), пока их нет — нода IPAdapter покажет ошибку.
4. Style weight по умолчанию 0.75, `weight_type = style transfer`, start 0.0 / end 1.0.
   Задача — переносить **стиль**, а не копировать Орка.

## ControlNet (позже)

В `..._CONTROL_TEMPLATE.json` ветка по умолчанию выключена: `ControlNetApplyAdvanced` в BYPASS,
препроцессоры (Canny / Lineart / DW-Pose) и `ControlNetLoader` в MUTE. Чтобы включить:
скачать веса → выбрать файл в `ControlNetLoader` → включить одну препроцессорную ноду →
снять BYPASS с `ControlNetApplyAdvanced` (Ctrl+B).

## Пересборка workflow

Правки стилевого контракта вносятся в `voxel_style_prompt_v1.json`, после чего workflow
пересобираются и проверяются серверным валидатором ComfyUI:

```powershell
$py = 'D:\programs\ComfyUI\python_embeded\python.exe'
& $py -s 'D:\Projects\CubeGame Factory\scripts\comfyui\build_factoria_voxel_workflows.py' `
   --object-info 'D:\Projects\CubeGame Factory\measurements\comfyui_object_info_2026-11-13_full.json' `
   --config 'D:\Projects\CubeGame Factory\workflows\factoria_voxel_style\voxel_style_prompt_v1.json' `
   --out 'D:\Projects\CubeGame Factory\workflows\factoria_voxel_style'
& $py -s 'D:\Projects\CubeGame Factory\scripts\comfyui\validate_factoria_workflows.py' `
   --comfy 'D:\programs\ComfyUI\ComfyUI' `
   --workflow-dir 'D:\Projects\CubeGame Factory\workflows\factoria_voxel_style' `
   --report 'D:\Projects\CubeGame Factory\measurements\factoria_voxel_style_validation.json'
```
