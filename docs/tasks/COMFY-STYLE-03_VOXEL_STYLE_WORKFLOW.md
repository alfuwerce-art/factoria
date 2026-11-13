# COMFY-STYLE-03 — FACTORIA VOXEL_STYLE workflow

**Проект:** Factoria · **Репозиторий:** `alfuwerce-art/factoria` · **Ветка:** `factory/work`
**Рабочая папка:** `D:\Projects\CubeGame Factory` · **Статус:** AUTHORIZED (2026-11-13)
**Основание:** FACT-D19. Документ восстановлен по утверждённому тексту ТЗ сессии 2026-11-13.

## Цель

Владелец сразу открывает готовый workflow и начинает тестировать фиксацию voxel-стиля
персонажей Factoria. Главный критерий: запустить ComfyUI → открыть Factoria workflow →
выбрать Orc reference → ввести character prompt → Queue → получить изображение →
увидеть реальный расход RAM/VRAM.

## Артефакты (в репозитории)

```
workflows/factoria_voxel_style/
  FACTORIA_VOXEL_STYLE_BASE.json              базовая генерация
  FACTORIA_VOXEL_STYLE_IPADAPTER.json         style reference через IPAdapter
  FACTORIA_VOXEL_STYLE_CONTROL_TEMPLATE.json  + отключаемая ветка ControlNet
  voxel_style_prompt_v1.json                  prompt contract (единый источник стиля)
  README.md                                    инструкция владельцу
scripts/comfyui/
  build_factoria_voxel_workflows.py           сборка workflow из contract + /object_info
  validate_factoria_workflows.py              проверка серверным validate_prompt
  factoria_launch.ps1                         запуск preset + измерение
  launch_safe_baseline.bat / launch_cpu_fallback.bat
```

## A. FACTORIA_VOXEL_STYLE_BASE.json

`CheckpointLoaderSimple → CLIPTextEncode(+/-) → EmptyLatentImage → KSampler → VAEDecode → SaveImage`.
Параметры: 512-class (512×768), batch = 1, без ControlNet, без IPAdapter, монитор ресурсов —
панель Crystools (глобальная для UI).

## B. FACTORIA_VOXEL_STYLE_IPADAPTER.json

Reference image задаёт **визуальный voxel-язык**. Готовые места: `LoadImage`, `CLIPVisionLoader`
(mute-слот), `IPAdapterUnifiedLoader`, `IPAdapterAdvanced`, style weight, start/end conditioning.
Если веса не установлены — workflow структурно готов, но не обязан запускаться.

## C. FACTORIA_VOXEL_STYLE_CONTROL_TEMPLATE.json

То же + отключаемая ветка ControlNet: Canny / Lineart (силуэт), DW-Pose (поза), Depth при
необходимости. ControlNet не обязателен для базовой генерации: по умолчанию ветка в BYPASS.

## Prompt contract

- **Stable style prefix (не менять):** stylized voxel/cuboid 3D character, hard-edged block
  geometry, blocks of varied sizes (large → silhouette, medium → anatomy/clothing, small →
  face/details), compact readable silhouette, modular limbs, pixel/block face, hard surfaces,
  no smooth organic sculpting, neutral studio presentation, пригодность для image-to-3D.
- **Variable character block:** race/species, sex, body type, face traits, clothing, armor,
  accessories, palette, pose, camera.
- **Negative (обязательно):** smooth plastic, rounded cartoon, anime, photorealistic skin,
  painterly, soft clay, chibi, fused limbs, Minecraft-style primitive cube-only body,
  cluttered background, extreme perspective, motion blur.

## Orc reference

Используется позже локально как style image. Не публикуется в GitHub, не встраивается в
workflow; workflow ожидает локальный файл в `ComfyUI/input/`. Цель — переносить стиль,
а не копировать Орка.

## Что должно сохраняться / меняться

Сохраняется: voxel/cuboid язык, размеры и иерархия блоков, уровень детализации лица,
жёсткие формы, характер пропорций, чистая студийная подача, отсутствие гладкой мультяшности.
Меняется: раса, лицо, одежда, броня, аксессуары, цвета, телосложение.

## Smoke test (разрешено исполнителю)

Запуск ComfyUI, проверка web UI/API, импорт custom nodes, отсутствие missing dependencies,
checkpoint detection, открытие/валидация workflow, Crystools, работа launch presets.
**Не** выполнять художественную генерацию Orc — первая реальная генерация и замер памяти
делаются после отчёта.

## Запрещено на этом этапе

Финальная 3D-модель, TripoSR, Blender geometry, rig, animation, emotions, Unity, batch
generation, десятки extensions, тяжёлые веса без необходимости, обучение LoRA и сбор датасета.
