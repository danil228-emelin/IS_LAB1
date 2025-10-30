# Flask Auth API with Security CI/CD
## API Endpoints
 Аутентификация
### POST /auth/login

Аутентификация пользователя и получение JWT токена.

Тело запроса:
```

{
  "username": "admin",
  "password": "Admin123!@#"
}

```
Успешный ответ:
```

{
  "success": true,
  "message": "Login successful",
  "data"
Соль генерируется автоматически

Проверка сложности паролей при регистрации

🔍 Security CI/CD Pipeline Автоматическое сканирование безопасности

При каждом push и pull request автоматически запускаются: SAST (Static Application Security Testing)

Bandit - статический анализ Python кода

Safety - проверка уязвимостей в зависимостях

Pylint - анализ качества кода

SCA (Software Composition Analysis)

pip-audit - аудит зависимостей Python

OWASP Dependency Check - комплексная проверка компонентов

Container Security: {
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


### Получение статистики системы, списка пользователей и последних постов.
Защищенные Endpoints (требуют JWT токен)<br>
GET /api/dat

Заголовки:
text<br>Flask Auth API with Security CI/CD
Authorization: Bearer <your_jwt_token><br>
Content-Type: application/json<br>
```
{
  "success": true,
  "message": "Data retrieved successfully",
  "data": {
    "stats": {
      "total_users": 5,
      "total_posts": 12,
      "your_posts": 3
    },
    "recent_posts": [
      {
        "id": "a1b2c3d4-e5f6-7890-abcd-ef1234567890",
        "title": "Добро пожаловать в наше приложение!",
        "content": "Это демонстрационный пост. Рады видеть вас здесь!",
        "user_id": "user-uuid-here",
        "author_username": "admin",
        "created_at": "2024-01-15T10:30:00",
        "updated_at": "2024-01-15T10:30:00",
        "is_published": true
      },
      {
        "id": "b2c3d4e5-f6g7-8901-bcde-f23456789012",
        "title": "Техническое обновление системы",
        "content": "Мы внедрили новые меры безопасности...",
        "user_id": "user-uuid-here",
        "author_username": "techuser",
        "created_at": "2024-01-14T15:45:00",
        "updated_at": "2024-01-14T15:45:00",
        "is_published": true
      }
    ],
    "users": [
      {
        "id": "user-uuid-1",
        "username": "admin",
        "email": "admin@example.com",
        "created_at": "2024-01-01T00:00:00"
      },
      {
        "id": "user-uuid-2",
        "username": "john_doe",
        "email": "john@example.com",
        "created_at": "2024-01-02T10:15:00"
      },
      {
        "id": "user-uuid-3",
        "username": "jane_smith",
        "email": "jane@example.com",
        "created_at": "2024-01-03T14:20:00"
      }
    ]
  }
}
```
Ошибки:
    401 Unauthorized - Токен отсутствует или невалиден
```
{
  "success": false,
  "message": "Token is missing"
}
```

  401 Unauthorized - Токен просрочен

```

{
  "success": false,
  "message": "Token has expired"
}
```
  404 Not Found - Пользователь не найден
```

{
  "success": false,
  "message": "User not found"
}
```
### Создание нового поста.
POST /api/posts


Заголовки:
text<br>
Authorization: Bearer <your_jwt_token> <br>
Content-Type: application/json <br>

Тело запроса:
```
{
  "title": "Заголовок поста",
  "content": "Содержимое поста"
}
```
## Защита от SQL Injection (SQLi)

Реализация:

    Использование SQLAlchemy ORM для всех запросов к базе данных

    Параметризованные запросы вместо конкатенации строк

    Автоматическое экранирование специальных символов

Пример  кода:
```
user = User.query.filter_by(username=username).first()
```

## Защита от XSS (Cross-Site Scripting)

Реализация:

    Санитизация HTML через html.escape() и библиотеку bleach

    Экранирование пользовательского ввода перед выводом в HTML

    Content Security Policy headers

    Автоматическая очистка опасных тегов и атрибутов

Пример защиты:

from utils import sanitize_html, sanitize_user_input

# Санитизация пользовательского ввода
safe_content = sanitize_html(user_input)
safe_data = sanitize_user_input(request_data)

## Защита аутентификации
JWT Токены

    Выдача JWT токенов при успешной аутентификации

    Время жизни токенов: 24 часа

Хэширование паролей

    Алгоритм: bcrypt с 12 раундами

    Соль генерируется автоматически

    Проверка сложности паролей при регистрации

🔍 Security CI/CD Pipeline
Автоматическое сканирование безопасности

При каждом push и pull request автоматически запускаются:
SAST (Static Application Security Testing)

    Bandit - статический анализ Python кода

    Safety - проверка уязвимостей в зависимостях

    Pylint - анализ качества кода

SCA (Software Composition Analysis)

    pip-audit - аудит зависимостей Python

    OWASP Dependency Check - комплексная проверка компонентов

Container Security

    Trivy - сканирование Docker образов на уязвимости

Security Testing

    pytest - автоматические тесты безопасности

    Интеграционные тесты - проверка механизмов защиты

  ## Отчеты безопасности
  <img width="971" height="306" alt="image" src="https://github.com/user-attachments/assets/89515f23-84bb-4438-a6c9-87356625fd61" />
  <img width="774" height="573" alt="image" src="https://github.com/user-attachments/assets/a167286b-6d6d-4fdc-9a1f-67f12ae197d7" />

