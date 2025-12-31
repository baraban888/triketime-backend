FROM python:3.12-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

CMD ["sh", "/app/start.sh"]
#ENV PORT=8080
#CMD ["sh", "-c", "gunicorn -b :$PORT app.main:app"]
#CMD ["gunicorn", "-b", ":$PORT", "wsgi:app"]
#CMD ["gunicorn", "-b :$PORT app.main:app"]
#CMD ["sh","-c","python -c 'import os; print(\"PORT=\", os.environ.get(\"PORT\"))' && python -c 'import app.main; print(\"import app.main OK\")' && gunicorn -b :$PORT app.main:app --log-level debug --access-logfile - --error-logfile -"]
#                          модуль ^   ^ имя переменной Flask-приложения
