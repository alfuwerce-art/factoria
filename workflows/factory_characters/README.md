# FACTORY CHARACTER GENERATION — как пользоваться

Этап COMFY-STYLE-05. Стиль **экспериментальный**: приёмка только владельцем.

## Файлы

| Файл | Назначение |
|---|---|
| `FACTORY_CHARACTER_GENERATION_V1.json` | **главный граф** (SDXL Turbo + FICTIVERSE LoRA, орк, 768×1024) |
| `FACTORY_CHARACTER_BASE.json` | режим сравнения BASE (без LoRA, нода в BYPASS) |
| `FACTORY_CHARACTER_FICTIVERSE.json` | режим FICTIVERSE (`VoxelXL_v1`, trigger `voxel style`) |
| `FACTORY_CHARACTER_RAL.json` | режим RAL (`ral-vxl`, trigger `ral-vxl`) — **только эксперимент** |
| `FACTORY_CHARACTER_IPADAPTER.json` | главный + блок IPAdapter (выключен, включается владельцем) |
| `FACTORY_CHARACTER_CONTROLNET.json` | главный + блок ControlNet union (выключен, включается владельцем) |
| `characters_v1.json` | конфиг персонажей (орк/человек/эльф), блоки промпта, ракурсы, сэмплинг |
| `factory_test_matrix_v1.json` | список прогонов для `factory_run_batch.py` |

## Запуск

```powershell
# 1) отдельный экземпляр ComfyUI под SDXL на 8190 (свой процесс; 8188 владельца не трогаем)
powershell -NoProfile -ExecutionPolicy Bypass -File `
  "...\scripts\comfyui\factoria_launch.ps1" -Preset xl -Port 8190 -DisableAssets -KeepRunning
# 2) UI → http://127.0.0.1:8190 → Workflow → Open → FACTORY_CHARACTER_GENERATION_V1.json
```

## Смена персонажа

Правится **только** текст блока CHARACTER в ноде `B/C/D/E. POSITIVE` (поля из `characters_v1.json`).
Стилевые блоки `BODY_STYLE_LOCK` / `FACE_STYLE_LOCK` и COMPOSITION не трогать — они и есть фиксация стиля.

## Смена режима

- FICTIVERSE ↔ RAL: изменить `lora_name` в ноде **STYLE LoRA** (`VoxelXL_v1.safetensors` ↔ `ral-vxl.safetensors`).
- BASE: перевести ноду **STYLE LoRA** в BYPASS (Ctrl+B).
- Сила LoRA: `strength_model` / `strength_clip` в той же ноде (стартовые 0.4 / 0.6 / 0.8).

## Блоки IPAdapter / ControlNet

По умолчанию выключены (BYPASS/MUTE) — граф работает без референса и без позы.
Включение IPAdapter: положить референс в `ComfyUI/input/`, выбрать его в `LoadImage`,
перевести `IPAdapter loader` и `IPAdapter apply` в ALWAYS.
Включение ControlNet: аналогично для `LoadImage` + один препроцессор (Canny / Lineart / DW-Pose)
+ `ControlNetLoader`, снять BYPASS с `ControlNet apply`.

## Важные ограничения (по факту измерений)

- На **SDXL Turbo CFG 2.0** LoRA FICTIVERSE практически не влияет; RAL влияет, но даёт «игрушечный» вид.
  Честная проверка LoRA — на обычном SDXL при CFG 5–7 (отдельное согласование).
- 1024×1024 не проходит при занятых ~1.5 ГБ VRAM сторонними приложениями; рабочий режим 768×1024.
- `ral-vxl` запрещает коммерческое использование и производные — результаты помечены в манифестах
  как `NOT_ALLOWED_EXPERIMENT_ONLY` и не публикуются.
