Ссылка на проект: https://github.com/SMolodtsova13/Auth_sprint_1

# 🚀 Auth Service

Сервис аутентификации и авторизации пользователей для онлайн-кинотеатра. Поддерживает регистрацию, вход, обновление токенов, выход, смену данных, историю входов и систему ролей для ограничения доступа к различным категориям контента.

## 📦 Технологии

[![Python 3.12+](https://img.shields.io/badge/-Python_3.12%2B-464646?style=flat&logo=Python&logoColor=56C0C0&color=008080)](https://www.python.org/)  
[![FastAPI](https://img.shields.io/badge/-FastAPI-464646?style=flat&logo=FastAPI&logoColor=56C0C0&color=008080)](https://fastapi.tiangolo.com/)  
[![PostgreSQL](https://img.shields.io/badge/-PostgreSQL-464646?style=flat&logo=PostgreSQL&logoColor=56C0C0&color=008080)](https://www.postgresql.org/)  
[![Redis](https://img.shields.io/badge/-Redis-464646?style=flat&logo=Redis&logoColor=56C0C0&color=008080)](https://redis.io/)  
[![SQLAlchemy 2.0](https://img.shields.io/badge/-SQLAlchemy_2.0-464646?style=flat&logo=sqlalchemy&logoColor=56C0C0&color=008080)](https://docs.sqlalchemy.org/)  
[![Alembic](https://img.shields.io/badge/-Alembic-464646?style=flat&logo=alembic&logoColor=56C0C0&color=008080)](https://alembic.sqlalchemy.org/)  
[![Docker](https://img.shields.io/badge/-Docker-464646?style=flat&logo=Docker&logoColor=56C0C0&color=008080)](https://www.docker.com/)  
[![Docker Compose](https://img.shields.io/badge/-Docker_Compose-464646?style=flat&logo=Docker&logoColor=56C0C0&color=008080)](https://docs.docker.com/compose/)  
[![JWT](https://img.shields.io/badge/-JWT-464646?style=flat&logo=JSON%20web%20tokens&logoColor=56C0C0&color=008080)](https://jwt.io/)  
[![ORJSON](https://img.shields.io/badge/-ORJSON-464646?style=flat&logo=Python&logoColor=56C0C0&color=008080)](https://github.com/ijl/orjson)  
[![Mypy](https://img.shields.io/badge/-Mypy-464646?style=flat&logo=Python&logoColor=56C0C0&color=008080)](http://mypy-lang.org/)  
[![PEP8](https://img.shields.io/badge/-PEP8-464646?style=flat&logo=Python&logoColor=56C0C0&color=008080)](https://peps.python.org/pep-0008/)  
[![Swagger (OpenAPI)](https://img.shields.io/badge/-Swagger_(OpenAPI)-464646?style=flat&logo=OpenAPI%20Initiative&logoColor=56C0C0&color=008080)](https://swagger.io/specification/)

## 📌 Функциональность

### 🔐 Аутентификация

- **Регистрация** (`/auth/register`)  
  - Валидация логина и пароля  
  - Хеширование пароля с помощью `werkzeug.security.generate_password_hash`  
    (PBKDF2-SHA256, соль длиной 16 байт)   
  - Обработка ошибок (дубликаты, слабый пароль)  
  - Сохранение в БД  

- **Вход** (`/auth/login`)  
  - Проверка логина и пароля  
  - Генерация JWT access и refresh токенов  
  - Сохранение refresh-токена в Redis с TTL  
  - Логирование входа (таблица `login_history`)  

- **Обновление access-токена** (`/auth/refresh`)  
  - Валидация refresh-токена из Redis  
  - Генерация нового access-токена  
  - Удаление старого refresh-токена  

- **Выход из аккаунта** (`/auth/logout`)  
  - Удаление конкретного refresh-токена  

- **Выход со всех устройств** (`POST /auth/logout/others`)  
  - Инвалидирует все **refresh**-токены пользователя (SCAN + DEL по ключу `refresh:{user_id}:*`)

### 👤 Работа с пользователем

- Получение истории входов (`/auth/me/history`)
- Изменение логина или пароля (`/auth/me/change`)
- Получение текущего профиля (`/auth/me`)

### 🛡️ Управление ролями

- Создание, удаление, обновление и просмотр ролей (`/roles/*`)
- Назначение/удаление ролей пользователю
- Проверка прав доступа пользователя
- Роли включаются в access-токен (ключ `roles`)

### ⚙️ Консольная команда

Для создания суперпользователя с правами администратора запустить команду:

```bash
python3 create_superuser.py
```

## 🧪 Запуск проекта

### 🐳 Через Docker

```bash
docker-compose up -d
```

Приложение будет доступно по адресу:

- **Приложение**: http://localhost:8000  
- **Документация Swagger**: http://localhost:8000/api/openapi  
- **OpenAPI JSON**: http://localhost:8000/api/openapi.json

### 🔄 Запуск миграций

```bash
docker-compose exec auth_service alembic upgrade head
```

## 🔐 Токены

- **Access токен** живёт 15 минут
- **Refresh токен** живёт 30 дней и хранится в Redis
- Токены подписываются по алгоритму `HS256`

## 📝 Changelog

- ✅ Регистрация с валидацией, хешированием, проверкой дубликатов
- ✅ Аутентификация, генерация токенов, логирование входа
- ✅ Обновление access-токена по refresh
- ✅ Logout одного устройства и всех
- ✅ История входов
- ✅ Изменение логина/пароля
- ✅ CRUD для ролей
- ✅ Назначение и удаление ролей
- ✅ Проверка прав пользователя
- ✅ Включение ролей в access-токен
- ✅ Консольная команда суперпользователя
- ✅ Swagger-документация
- ✅ Запуск через Docker

## 👥 Команда

[Светлана Молодцова](https://github.com/SMolodtsova13)  
[Анна Пестова](https://github.com/Anna9449)  
[Анна Зыбель](https://github.com/AnnZebel)  
---
