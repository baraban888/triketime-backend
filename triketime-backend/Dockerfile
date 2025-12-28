FROM python:3.12-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

ENV PORT=8080

# Было (неправильно):
# CMD ["gunicorn", "-b", "0.0.0.0:8080", "app.main:create_app()"]
# или "app.main:create_app"

# Должно быть:
CMD ["gunicorn", "-b", "0.0.0.0:8080", "app.main:app"]
#                          модуль ^   ^ имя переменной Flask-приложения
