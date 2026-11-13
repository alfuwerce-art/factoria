# TOOL_INVENTORY — CubeGame Factory Lab

**Снимок системы:** 2026-11-13 11:43 (Europe/Moscow)
**Этап:** PREP-00 — аудит ПК и установленного ПО
**Доказательство:** `logs/PREP-00_detection_2026-11-13.txt` — реальный вывод команд (177 строк).
**Важно:** в рамках PREP-00 **ничего не устанавливалось и не скачивалось**. Всё ниже — результат обнаружения на машине, а не план.

---

## 1. Аппаратная база (подтверждена)

| Параметр | Факт | Комментарий для Factory |
|---|---|---|
| Машина | ASUS TUF Gaming A17 FA707NV, x64 | ноутбук |
| ОС | Windows 11 Pro, 10.0.26200 (build 26200), x64 | установлена 2026-06-03, последняя загрузка 2026-11-13 04:14 |
| CPU | AMD Ryzen 5 7535HS, 6 ядер / 12 потоков, 3.3 ГГц, L3 16 МБ | пересчёт скинов, Rigify, рендер — реально ограничены 6 ядрами; GPU-тяжёлые задачи важны |
| RAM | 32 ГБ = 2 × 16 ГБ Samsung DDR5-5600; доступно ОС 31.24 ГБ | на момент аудита свободно **18.67 ГБ** |
| GPU (дискретная) | **NVIDIA GeForce RTX 4060 Laptop, 8188 MiB VRAM** | драйвер **610.47** (2026-05-19), CUDA UMD 13.3; занято 1251 MiB, **свободно 6706 MiB**, 57 °C |
| GPU (встроенная) | AMD Radeon (в CPU 7535HS), ~0.5 ГБ | для Factory не используется |
| Диск C: | NTFS, 475.9 ГБ, **свободно 68.2 ГБ** | тесно; крупные веса и кэши сюда не ставить |
| Диск D: | NTFS, 953.9 ГБ, **свободно 642.1 ГБ** | основной диск для инструментов, сэмплов и AI-весов |
| PowerShell | Windows PowerShell 5.1.26100.9818 (pwsh 7 отсутствует) | все команды в журналах — PS 5.1; учитывать кодировку UTF-16 в `Tee-Object` |

**Вывод по железу:** конфигурация соответствует ТЗ (RTX 4060 Laptop 8 ГБ VRAM, 32 ГБ RAM). Ограничения: 8 ГБ VRAM (~6.7 ГБ фактически свободно) — локальные AI-модели только по одной за раз, тяжёлые 3D/AI-кандидаты проверять документально до скачивания. Место: D: достаточно, C: не использовать для весов.

---

## 2. Обнаруженные инструменты

| Компонент | Версия | Фактический путь | Источник установки | Статус | Примечание |
|---|---|---|---|---|---|
| Python (3.13) | **3.13.14** (64-bit) | `C:\Users\bow\AppData\Local\Programs\Python\Python313\python.exe` | python.org (user install) | DETECTED | в PATH первым; `venv` работает (`import venv` OK) |
| Python (3.14) | 3.14.6 | `C:\Users\bow\AppData\Local\Python\pythoncore-3.14-64\python.exe` | python.org / Python Manager | DETECTED | доступен через `py -3.14`; **не** использовать для Lab без причины |
| pip | 26.1.2 | `...\Python313\Scripts\pip.exe` | вместе с Python | DETECTED | в глобальном окружении 47 пакетов; `torch`/`numpy` **отсутствуют** (чистая база, не AI-окружение) |
| Git | **2.55.0.windows.1** | `C:\Program Files\Git\cmd\git.exe` | git-scm.com | DETECTED | `user.name` / `user.email` **не настроены** — commit невозможен без локальной настройки |
| VS Code | **1.145.2** | `C:\Users\bow\AppData\Local\Programs\Microsoft VS Code\bin\code.cmd` | Microsoft | DETECTED | редактор кода/логов |
| Unity Hub | **3.22.5** | `D:\Unity Hub\Unity Hub.exe` | Unity Technologies | DETECTED_NOT_TESTED | только обнаружение, не запускался |
| Unity Editor | **6000.3.27f2** | `D:\Unity\Hub\Editor\6000.3.27f2\Editor\Unity.exe` | Unity Hub | DETECTED_NOT_TESTED | целевая LTS-линия из ТЗ присутствует |
| Unity Editor | 6000.6.7f1 | `D:\Unity\6000.6.7f1\Editor\Unity.exe` | Unity (отдельно от Hub) | DETECTED_NOT_TESTED | вторая версия; **не открывать** CubeGame на этом этапе |
| Ollama | **0.40.10** | `C:\Users\bow\AppData\Local\Programs\Ollama\ollama.exe` | ollama.com | DETECTED_NOT_RUNNING | API `127.0.0.1:11434` не отвечает, процесс не запущен |
| .NET Runtimes | 7.0.14, 8.0.34 | `C:\Program Files\dotnet\` | Microsoft | DETECTED | нужны некоторым GUI/CLI-утилитам |
| WinRAR | 7.13 | `C:\Program Files\WinRAR` | win.rar GmbH | DETECTED | может распаковать Blender `.zip`; `Expand-Archive` тоже доступен |
| NVIDIA App / драйвер | 610.47 | `C:\Program Files\NVIDIA Corporation\` | NVIDIA | DETECTED | CUDA UMD 13.3; **CUDA Toolkit (nvcc) отсутствует** |

---

## 3. Отсутствующие инструменты (подтверждено поиском)

| Компонент | Статус | Как проверялось | Что это значит |
|---|---|---|---|
| **Blender** | **NOT_FOUND** | нет в PATH, нет в реестре Uninstall, `blender.exe` не найден (рекурсивный поиск C:\ и D:\ до глубины 4) | **главный блокер PREP-01**: ядро конвейера (геометрия, armature, skinning, анимация, CLI) отсутствует |
| **Rigify** | N/A | часть Blender | проверить сразу после установки Blender |
| **ComfyUI** | **NOT_FOUND** | нет каталога `*omfy*` на C:\ и D:\ (глубина 3–4), нет ярлыков в Start Menu/Desktop, нет записи в реестре, порт 8188 не слушается, `run_nvidia_gpu*.bat` не найден | **расхождение с ТЗ/памятью**, где ComfyUI указан как имеющийся (`USER_REPORTED`). Требуется путь от пользователя либо согласованная установка |
| **Cascadeur** | **NOT_INSTALLED** | нет `Cascadeur*.exe`, нет в реестре | кандидат PREP-05; до установки проверить лицензию |
| **n8n** | **NOT_INSTALLED** | нет в PATH/реестре | плюс: **системного Node.js/npm нет** — n8n потребовал бы установку Node.js (не делать без доказанной необходимости) |
| **Node.js / npm / pnpm** | **NOT_FOUND** (системный) | нет в PATH | связка `node` встречается только внутри Codex runtime и не является системным инструментом |
| **ffmpeg** | NOT_FOUND (в PATH) | нет команды | может понадобиться для превью/видео; не блокер |
| **7-Zip** | STALE_REGISTRY | запись Uninstall указывает `D:\programs\7-Zip\`, но каталога и `7z.exe` нет | считать неустановленным, не полагаться |
| **CUDA Toolkit** | NOT_FOUND | `nvcc` отсутствует | для ComfyUI/PyTorch обычно достаточно драйвера + CUDA-сборки wheel; отдельный Toolkit пока не нужен |

---

## 4. Ограничения, конфликты и ловушки

1. **`python3` — ловушка Windows.** `C:\Users\bow\AppData\Local\Microsoft\WindowsApps\python3.exe` — Store-заглушка, отвечает «Python was not found». В скриптах использовать только `python` или `py -3.13`, никогда `python3`.
2. **Два Python.** 3.13.14 (в PATH, по умолчанию) и 3.14.6 (через `py`). Для Lab использовать **изолированный venv на 3.13.14** и фиксировать версию; 3.14 не трогать.
3. **Глобальное Python-окружение уже содержит 47 сторонних пакетов** (крипто/VPN-утилиты). Ничего в него не устанавливать — только `venv` в `environments\`.
4. **Git-идентичность не задана.** `git config user.name/user.email` пустые → первый commit упадёт. Настроить **локально в репозитории** (не глобально) при первой фиксации.
5. **C: почти заполнен (68.2 ГБ).** Blender и любые веса — на D:.
6. **Глобальные изменения запрещены:** PATH, драйверы, CUDA, переменные окружения не менялись и не должны меняться на этом этапе.
7. **Посторонний фон:** на момент аудита работали браузеры, ChatGPT/Codex, Happ, DeepSeek Harness, wallpaper engine. Они держат ~1.25 ГБ VRAM из 8. Чужие процессы **не останавливались**. Для AI-тестов позже учитывать фактически свободные ~6.7 ГБ VRAM, а не 8.
8. **`D:\Games\CubeGame`** — игровая установка, а **`D:\Projects\CubeGame`** — рабочий репозиторий CubeGame (`.git` подтверждён). Оба вне лаборатории и не затрагивались.
9. **Каталог проекта (актуально с 2026-11-13 12:05 MSK):** единственная рабочая папка — `D:\Projects\CubeGame Factory`. Она содержит четыре документа, журналы `docs/`, доказательства `logs/` и git-репозиторий. Ранее созданный `D:\Projects\CubeGameFactoryLab` — архив прошлой сессии, для новой работы не использовать (SUPERSEDED, FACT-D16 в памяти).

---

## 5. Что этим аудитом НЕ доказано

- Что Blender работает (его нет).
- Что Rigify/auto-weights/skinning дают пригодный результат.
- Что ComfyUI существует и запускается.
- Что Unity открывает экспортированные FBX (CubeGame и Unity не запускались — запрещено).
- Совместимость каких-либо AI-моделей с 8 ГБ VRAM.

Эти пункты закрываются на PREP-01…PREP-05 и требуют реальных запусков.
