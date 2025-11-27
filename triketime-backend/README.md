# TrikeTime Backend (Flask + Google Cloud Run)

## 🚀 Описание
Backend для мобильного приложения TrikeTime.
Сервис предоставляет REST API для регистрации пользователей, смен, вождения, перерывов.

## 🛠 Stack
- Python 3.12
- Flask
- Docker
- Google Cloud Run

## ▶ Локальный запуск
python app/main.py

csharp
Копировать код

Откроется на:
http://127.0.0.1:8080

## ▶ API тест
GET /api/health

shell
Копировать код

## ▶ Docker билд
docker build -t triketime-backend .
docker run -p 8080:8080 triketime-backend