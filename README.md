# API

После запуска приложение будет доступно по адресу: http://localhost:5000

1. Аутентификация:
```

curl -X POST http://localhost:5000/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username": "admin", "password": "admin123"}'
```
2. Получение данных:

```
curl -X GET http://localhost:5000/api/data \
  -H "Authorization: Bearer YOUR_JWT_TOKEN"
```
3. Создание поста:
```

curl -X POST http://localhost:5000/api/posts \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  -d '{"title": "Мой пост из Docker", "content": "Содержимое поста созданного внутри контейнера"}'
```
# Deploy

 Docker Compose создает:

    Flask приложение с JWT аутентификацией

    SQLite базу данных внутри контейнера


# API Endpoints Примеры
1. Аутентификация
POST /auth/login

Аутентификация пользователя.

Тело запроса:
```

{
  "username": "admin",
  "password": "admin123"
}

Успешный ответ:
json

{
  "success": true,
  "message": "Login successful",
  "data": {
    "access_token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
    "token_type": "bearer",
    "user": {
      "id": "uuid",
      "username": "admin",
      "email": "admin@example.com",
      "created_at": "2024-01-01T00:00:00",
      "is_active": true
    }
  }
}

```
2. Защищенные endpoints (требуют JWT токен)
GET /api/data

Получение статистики и данных системы.

Заголовки:
text

Authorization: Bearer <your_jwt_token>

Ответ:
```

{
  "success": true,
  "message": "Data retrieved successfully",
  "data": {
    "stats": {
      "total_users": 5,
      "total_posts": 10,
      "your_posts": 3
    },
    "recent_posts": [...],
    "users": [...]
  }
}
```
POST /api/posts (требуют JWT токен) 

Создание нового поста.

Заголовки:

Authorization: Bearer <your_jwt_token>
Content-Type: application/json

Тело запроса:
```

{
  "title": "Заголовок поста",
  "content": "Содержимое поста"
}
```


При первом запуске автоматически создаются тестовые пользователи:
Username	Password	Email
admin	admin123	admin@example.com
testuser	test123	test@example.com


# Структура проекта
text

flask-auth-app/
├── docker-compose.yml    # Docker Compose конфигурация
├── Dockerfile           # Конфигурация Docker образа
├── requirements.txt     # Python зависимости
├── app.py              # Основное приложение Flask
├── config.py           # Конфигурация приложения
├── .env               # Переменные окружения
└── README.md          # Документация