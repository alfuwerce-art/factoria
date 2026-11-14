# COMFY-STYLE-06 — RUN REPORT (SDXL Base 1.0 + Fictiverse Voxel XL)

**Дата:** 2026-11-14 · **Ветка:** `factory/work` · **Исполнитель:** DeepSeek
**Основание:** COMFY-STYLE-05 провалил визуальную приёмку (на SDXL-Turbo при CFG 2.0 LoRA Fictiverse не работала).
**Статус: SUPERSEDED by COMFY-STYLE-07.** Этап был остановлен на незавершённой загрузке `sd_xl_base_1.0.safetensors` (291 МБ из 6.94 ГБ на момент прерывания). Работа продолжилась в `COMFY-STYLE-07_RUN_REPORT.md`: там тот же официальный чекпоинт докачивается, а генерация строится не на LoRA, а на утверждённых референсах персонажей (IPAdapter / ControlNet / img2img). Файлы V2 (`FACTORY_CHARACTER_SDXL_BASE_V2*.json`) сохранены как заготовка LoRA-сравнения и в этом этапе не использовались; plumbing-прогон `plumb_runner_v2` выполнялся на DreamShaper XL Turbo (4 шага, CFG 2) и не является результатом сравнения.


---

## 1. Что сделано

| Пункт ТЗ | Результат |
|---|---|
| 1. Официальный SDXL Base 1.0 | `stabilityai/stable-diffusion-xl-base-1.0`, файл `sd_xl_base_1.0.safetensors`, 6 938 078 334 B, SHA-256 `31e35c80fc4829d14f90153f4c74cd59c90b779f6afe05a74cd6120b893f7e5b`, лицензия **openrail++** |
| 2. Сохранность DreamShaper XL Turbo и старых workflow | оба checkpoint'а лежат рядом в `models/checkpoints`; `FACTORY_CHARACTER_*`, `DREAMSHAPER_XL_*`, `FACTORIA_VOXEL_STYLE_*` не изменялись |
| 3. Новый workflow | `workflows/factory_characters/FACTORY_CHARACTER_SDXL_BASE_V2.json` (+ `_DIAG` с коротким промптом) |
| 4. Fictiverse Voxel XL на SDXL Base | `LoraLoader` (`VoxelXL_v1.safetensors`, trigger `voxel style`) между checkpoint и CLIP/KSampler |
| 5. Диапазон настроек | steps 25–30 (по умолчанию 28), CFG 5–7 (по умолчанию 6.0), LoRA 0.4 / 0.6 / 0.8 |
| 6. Sampler/scheduler по тестам | см. §3 |
| 7. Короткий диагностический тест | `FACTORY_CHARACTER_SDXL_BASE_V2_DIAG.json` + прогон `v2_diag_short` |
| 8. Исключение character sheet / нескольких фигур | усиленный negative: `character sheet, turnaround, multiple views, multiple characters, two characters, three characters, collage, split image, repeated figures, duplicate` + `single character only, one figure` в COMPOSITION |
| 9. Проверка лица/геометрии/текстур/тела/A-pose | см. §4 (техническая оценка, художественной приёмки нет) |
| 10. RAM / VRAM / время | см. §3 (реальные замеры) |
| 11. Контактный лист + отчёт | `outputs/factory/characters_v2/contact_sheet.png`, этот отчёт |
| RAL LoRA | **не применяется** (FACT-D21); в матриксе этапа отсутствует |

## 2. Файлы

```
workflows/factory_characters/
  FACTORY_CHARACTER_SDXL_BASE_V2.json        структурированный длинный промпт
  FACTORY_CHARACTER_SDXL_BASE_V2_DIAG.json   короткий диагностический промпт
  sdxl_base_v2.json                          конфиг модели/сэмплинга/промптов
  factory_test_matrix_v2.json                матрикс прогонов (sampler / CFG / LoRA / short-vs-long)
scripts/comfyui/
  build_factory_v2_workflow.py               сборка графов + матрикса из конфига
  factory_run_batch.py                       раннер: оверрайды, телеметрия, манифесты
  factory_contact_sheet.py                   контактный лист
outputs/factory/characters_v2/               PNG + <run>.manifest.json (локально)
measurements/factory_batch_report_v2.json    метрики всех прогонов
```

## 3. Прогоны и метрики

_(заполняется после завершения загрузки checkpoint и прогонов)_

## 4. Техническая оценка изображений

_(заполняется; художественная приёмка — только владелец)_

## 5. Ограничения

- 1024×1024 не проверяется: на 8 ГБ VRAM при занятых ~1.5 ГБ сторонними приложениями не влезает.
- Независимого регионального управления BODY/FACE нет — только текстовые блоки.
- Fictiverse лицензия openrail: коммерческое использование требует отдельной проверки.
