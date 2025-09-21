# Face Blur Lab (VS Code)

Задание на 5 баллов: распознать **лицо**, выделить **овалом**, выделить **глаза** кружками, **размыть лицо кроме глаз**, *опционально* — наложить **очки**.

## Быстрый старт (VS Code)

1. Открой папку проекта `face-blur-lab` в VS Code.
2. Установи интерпретатор Python 3.10+ (подойдёт и 3.8+).
3. Создай виртуальное окружение:
   - Windows PowerShell:
     ```powershell
     python -m venv .venv
     .\.venv\Scripts\Activate.ps1
     ```
   - macOS/Linux:
     ```bash
     python3 -m venv .venv
     source .venv/bin/activate
     ```
4. Установи зависимости:
   ```bash
   pip install -r requirements.txt
   ```
5. Положи фронтальное фото актёра/актрисы в `images/` под именем **actor.jpg** (чем больше и чётче — тем лучше).
6. (Опционально) Замени `images/sunglasses.png` на свои очки (PNG с прозрачностью).
7. Запусти конфигурацию **Run face blur lab** (Run and Debug) или через терминал:
   ```bash
   python src/main.py
   ```

Результаты появятся в папке `images/`:
- `debug_shapes.jpg` — овал и кружки для глаз
- `result_blur_no_glasses.jpg` — лицо размыто, глаза чёткие
- `result_blur_with_glasses.jpg` — как выше + очки

## Трюки и отладка

- Если лицо не находится: используй фронтальное фото, без сильных наклонов и крупных очков; попробуй увеличить изображение или изменить параметры `scaleFactor`/`minNeighbors` в коде.
- Если глаза не находятся: на некоторых фото срабатывают брови — в коде стоит фильтр по вертикали (верхние 2/3 лица). Можно ослабить: `if ey + eh/2 < fh * 0.75`.
- Сила размытия: параметр `BLUR_KSIZE` (чем больше ядро, тем сильнее размытие).

## Структура
```
face-blur-lab/
  .vscode/launch.json
  images/
    sunglasses.png         # PNG с альфой (в комплекте)
    actor.jpg              # добавь своё фото
  src/
    main.py                # основной скрипт
  requirements.txt
  .gitignore
  README.md
```