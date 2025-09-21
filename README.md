# face-blur
# 1) Создать виртуальное окружение (если ещё не)
py -3 -m venv .venv
# альтернативно:
# python -m venv .venv

# 2) Обновить pip внутри окружения (через явный интерпретатор venv)
.\.venv\Scripts\python.exe -m ensurepip --upgrade
.\.venv\Scripts\python.exe -m pip install --upgrade pip

# 3) Поставить зависимости
.\.venv\Scripts\python.exe -m pip install -r requirements.txt

# 4) Запустить скрипт
.\.venv\Scripts\python.exe src/main.py
