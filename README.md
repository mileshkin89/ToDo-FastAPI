# ToDo-FastAPI

## ✨ Table of Contents

- [📋 Overview](#-overview)
- [✨ Features](#-features)
- [📦 Installation](#-installation)
- [📖 Usage Guide](#-usage-guide)
- [🔌 API Routes](#-api-routes)
- [📁 Project Structure](#-project-structure)
- [🛠️ Tech Stack](#-tech-stack)
- [📝 List of Versions](#-list-of-versions)
- [📄 License](#-license)

---

## 📋 Overview

ToDo-FastAPI is a modern REST API application for task management built on FastAPI. The project provides a full-featured task management system with authentication, authorization, analytics, and administrative functions.

The application uses an asynchronous architecture to ensure high performance and scalability. PostgreSQL database is used for data storage, and Redis is used for caching analytical data.

## ✨ Features

### 🔐 Authentication and Authorization
- User registration
- Login using OAuth2
- JWT tokens (access and refresh)
- Automatic token refresh
- Secure password storage using Argon2
- Protected routes with access control

### ✅ Task Management
- Create, read, update, and delete tasks
- Filter tasks by completion status
- Search tasks by title and description
- Sort tasks by various fields
- Pagination of results
- Toggle task completion status
- Set start, completion, and due dates

### 📊 Analytics
- Global analytics for all tasks
- User-specific analytics
- Aggregated statistics for various periods
- Caching of analytical data in Redis

### 👑 Administrative Functions
- Superuser creation
- User and task management
- Extended access rights for administrators

### 🔧 Additional Features
- Automatic database migrations with Alembic
- Docker containerization for easy deployment
- Full test coverage
- Automatic API documentation (Swagger/OpenAPI)
- Support for multiple environments (development, testing, production)

## 📦 Installation

### 🐳 Installation via Docker (Recommended)

1. Clone the repository:
```bash
git clone https://github.com/mileshkin89/ToDo-FastAPI.git
cd Smart-ToDo-FastAPI
```

2. Create a `.env` file based on `.env.sample`:
```bash
cp .env.sample .env
```

3. Fill in the environment variables in the `.env` file:
```env
# PostgreSQL
POSTGRES_DB=your_database_name
POSTGRES_DB_PORT=5432
POSTGRES_USER=your_username
POSTGRES_PASSWORD=your_password
POSTGRES_HOST=db

# JWT / Auth
SECRET_KEY=your_secret_key_here
REFRESH_SECRET_KEY=your_refresh_secret_key_here
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=15
REFRESH_TOKEN_EXPIRE_DAYS=7

# Redis
REDIS_HOST=redis
REDIS_PORT=6379
REDIS_DB=0

# Environment
ENVIRONMENT=development
```

4. Build and start the containers:
```bash
make build
make up
```

5. Apply database migrations:
```bash
make migrate
```

6. (Optional) Create a superuser:
```bash
make create_superuser
```

7. (Optional) Populate the database with test data:
```bash
make seed
```

### 💻 Installation without Docker

1. Install dependencies:
```bash
pip install uv
uv pip install -r pyproject.toml
```

2. Install and configure PostgreSQL and Redis

3. Create a `.env` file with the necessary environment variables

4. Apply migrations:
```bash
alembic upgrade head
```

5. Run the application:
```bash
uvicorn src.app:app --host 0.0.0.0 --port 8000 --reload
```

## 📖 Usage Guide

### 🚀 Running the Application

After installation, the application will be available at:
- API: http://localhost:8000
- Swagger Documentation: http://localhost:8000/docs
- Alternative ReDoc Documentation: http://localhost:8000/redoc

### ⚙️ Main Makefile Commands

```bash
make help          # Show all available commands
make build         # Build Docker containers
make up            # Start all services
make down          # Stop all services
make logs          # Show container logs
make restart       # Restart services
make migrate       # Apply database migrations
make seed          # Populate database with test data
make create_superuser  # Create superuser
```

### 💡 API Usage Examples

#### 👤 User Registration
```bash
curl -X POST "http://localhost:8000/api/v1/auth/register" \
  -H "Content-Type: application/json" \
  -d '{
    "email": "user@example.com",
    "name": "John Doe",
    "password": "securepassword123"
  }'
```

#### 🔑 Login
```bash
curl -X POST "http://localhost:8000/api/v1/auth/token" \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=user@example.com&password=securepassword123"
```

#### ➕ Create Task
```bash
curl -X POST "http://localhost:8000/api/v1/tasks" \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "title": "New Task",
    "description": "Task description"
  }'
```

#### 📝 Get Task List
```bash
curl -X GET "http://localhost:8000/api/v1/tasks?skip=0&limit=10&completed=false" \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN"
```

#### 📈 Get Analytics
```bash
curl -X GET "http://localhost:8000/api/v1/analytics/users_global" \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN"
```

### 🧪 Testing

Run tests:
```bash
pytest src/tests/
```

Run tests with coverage:
```bash
pytest src/tests/ --cov=src --cov-report=html
```

## 🔌 API Routes

All API endpoints use the `/api/v1` prefix. Protected routes require a JWT token in the `Authorization: Bearer <token>` header.

### 🔐 Authentication (`/api/v1/auth`)

#### `POST /api/v1/auth/register`
Register a new user.

**Request Body:**
```json
{
  "email": "user@example.com",
  "name": "John Doe",
  "password": "securepassword123",
  "repeat_password": "securepassword123"
}
```

**Response:** `201 Created`
```json
{
  "id": 1,
  "email": "user@example.com",
  "name": "John Doe",
  "is_active": true,
  "last_login": null
}
```

#### `POST /api/v1/auth/token`
Login and get access tokens.

**Request Body:** (form-data)
- `username`: user email
- `password`: password

**Response:** `200 OK`
```json
{
  "access_token": "eyJ0eXAiOiJKV1QiLCJhbGc...",
  "token_type": "bearer"
}
```

Refresh token is automatically set in HTTP-only cookie.

#### `POST /api/v1/auth/token/refresh`
Refresh access token using refresh token from cookie.

**Response:** `200 OK`
```json
{
  "access_token": "eyJ0eXAiOiJKV1QiLCJhbGc...",
  "token_type": "bearer"
}
```

#### `POST /api/v1/auth/logout`
Logout from the system. Requires authentication.

**Response:** `200 OK`
```json
{
  "message": "Successfully logged out"
}
```

### ✅ Tasks (`/api/v1/tasks`)

All task routes require authentication.

#### `GET /api/v1/tasks`
Get list of current user's tasks with filtering, search, sorting, and pagination.

**Query Parameters:**
- `completed` (bool, optional): Filter by completion status
- `q` (string, optional): Search by title or description
- `skip` (int, default=0): Number of records to skip
- `limit` (int, default=10, max=100): Record limit
- `sort_by` (string, default="created_at"): Field to sort by
- `sort_order` (string, default="desc"): Sort order (asc/desc)

**Response:** `200 OK`
```json
{
  "tasks": [
    {
      "id": 1,
      "title": "New Task",
      "description": "Task description",
      "completed": false,
      "created_at": "2025-01-15T10:00:00Z",
      "updated_at": "2025-01-15T10:00:00Z",
      "start_at": null,
      "completed_at": null,
      "due_date": null
    }
  ],
  "pagination": {
    "total": 50,
    "skip": 0,
    "limit": 10,
    "has_more": true
  }
}
```

#### `POST /api/v1/tasks`
Create a new task.

**Request Body:**
```json
{
  "title": "New Task",
  "description": "Task description",
  "completed": false,
  "start_at": "2025-01-20T10:00:00Z",
  "due_date": "2025-01-25T18:00:00Z"
}
```

**Response:** `201 Created`
```json
{
  "id": 1,
  "title": "New Task",
  "description": "Task description",
  "completed": false,
  "created_at": "2025-01-15T10:00:00Z",
  "updated_at": "2025-01-15T10:00:00Z",
  "start_at": "2025-01-20T10:00:00Z",
  "completed_at": null,
  "due_date": "2025-01-25T18:00:00Z"
}
```

#### `GET /api/v1/tasks/{task_id}`
Get a specific task by ID. Available only to the task owner or administrator.

**Response:** `200 OK`
```json
{
  "id": 1,
  "title": "New Task",
  "description": "Task description",
  "completed": false,
  "created_at": "2025-01-15T10:00:00Z",
  "updated_at": "2025-01-15T10:00:00Z",
  "start_at": null,
  "completed_at": null,
  "due_date": null
}
```

#### `PUT /api/v1/tasks/{task_id}`
Full update of a task. Available only to the task owner or administrator.

**Request Body:**
```json
{
  "title": "Updated Title",
  "description": "Updated description",
  "start_at": "2025-01-20T10:00:00Z",
  "due_date": "2025-01-25T18:00:00Z"
}
```

**Response:** `200 OK` - Updated task

#### `PATCH /api/v1/tasks/{task_id}/toggle`
Toggle task completion status. Available only to the task owner or administrator.

**Response:** `200 OK` - Task with updated status

#### `DELETE /api/v1/tasks/{task_id}`
Delete a task. Available only to the task owner.

**Response:** `204 No Content`

### 📊 Analytics (`/api/v1/analytics`)

All analytics routes require authentication.

#### `GET /api/v1/analytics/global`
Get global statistics for all tasks in the system.

**Response:** `200 OK`
```json
{
  "counters": {
    "total_tasks": 1000,
    "active_tasks": 750,
    "completed_tasks": 200,
    "overdue_tasks": 50,
    "total_users": 100
  }
}
```

#### `GET /api/v1/analytics/global_aggregated`
Get aggregated global statistics for a period.

**Query Parameters:**
- `period` (string, default="7d"): Aggregation period (24h, 7d, 30d)

**Response:** `200 OK` - Statistics for the specified period

#### `GET /api/v1/analytics/users_global`
Get statistics for tasks of all users.

**Response:** `200 OK`
```json
{
  "counters": [
    {
      "user_id": 1,
      "total_tasks": 50,
      "active_tasks": 30,
      "completed_tasks": 15,
      "overdue_tasks": 5,
      "overdue_percent": 10.0
    }
  ]
}
```

#### `GET /api/v1/analytics/users_aggregated`
Get aggregated statistics for users over a period.

**Query Parameters:**
- `period` (string, default="7d"): Aggregation period (24h, 7d, 30d)

**Response:** `200 OK` - Aggregated user statistics

### 👑 Administrative Functions (`/api/v1/admin`)

All administrative routes require superuser privileges.

#### `GET /api/v1/admin/users`
Get list of all users with filtering, search, sorting, and pagination.

**Query Parameters:**
- `active` (bool, optional): Filter by user active status
- `q` (string, optional): Search by name or email
- `skip` (int, default=0): Number of records to skip
- `limit` (int, default=10, max=100): Record limit
- `sort_by` (string, default="registered_at"): Field to sort by (registered_at, last_login, id)
- `sort_order` (string, default="desc"): Sort order (asc/desc)

**Response:** `200 OK`
```json
{
  "users": [
    {
      "id": 1,
      "email": "user@example.com",
      "name": "John Doe",
      "is_active": true,
      "last_login": "2025-01-15T10:00:00Z"
    }
  ],
  "pagination": {
    "total": 100,
    "skip": 0,
    "limit": 10,
    "has_more": true
  }
}
```

#### `GET /api/v1/admin/users/{user_id}`
Get information about a specific user.

**Response:** `200 OK` - User information

#### `PATCH /api/v1/admin/users/{user_id}/deactivate`
Deactivate a user.

**Response:** `200 OK` - Updated user information

#### `PATCH /api/v1/admin/users/{user_id}/activate`
Activate a user.

**Response:** `200 OK` - Updated user information

#### `GET /api/v1/admin/users/{user_id}/tasks`
Get all tasks of a specific user with filtering, search, sorting, and pagination.

**Query Parameters:**
- `completed` (bool, optional): Filter by completion status
- `q` (string, optional): Search by title or description
- `skip` (int, default=0): Number of records to skip
- `limit` (int, default=10, max=100): Record limit
- `sort_by` (string, default="created_at"): Field to sort by (created_at, start_at, completed_at, due_date, id)
- `sort_order` (string, default="desc"): Sort order (asc/desc)

**Response:** `200 OK`
```json
{
  "user": {
    "id": 1,
    "email": "user@example.com",
    "name": "John Doe",
    "is_active": true,
    "last_login": "2025-01-15T10:00:00Z"
  },
  "tasks": [
    {
      "id": 1,
      "title": "User Task",
      "description": "Description",
      "completed": false,
      "created_at": "2025-01-15T10:00:00Z",
      "updated_at": "2025-01-15T10:00:00Z",
      "start_at": null,
      "completed_at": null,
      "due_date": null
    }
  ],
  "pagination": {
    "total": 50,
    "skip": 0,
    "limit": 10,
    "has_more": true
  }
}
```

### 🏠 Root Routes

#### `GET /`
API health check.

**Response:** `200 OK`
```json
{
  "message": "ToDo API is running"
}
```

#### `GET /protected`
Protected route for authentication check. Requires JWT token.

**Response:** `200 OK`
```json
{
  "message": "This is a protected route",
  "user_email": "user@example.com",
  "user_id": 1
}
```

### 📚 API Documentation

- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

## 📁 Project Structure

```
Smart-ToDo-FastAPI/
├── src/                          # Application source code
│   ├── app.py                    # Main FastAPI application file
│   ├── settings.py               # Application settings
│   ├── apps/                     # Application modules
│   │   ├── auth/                 # Authentication and authorization
│   │   │   ├── routes.py         # Authentication routes
│   │   │   ├── dependencies.py   # Authentication dependencies
│   │   │   ├── jwt.py            # JWT token handling
│   │   │   └── utils.py          # Cookie utilities
│   │   ├── task/                 # Task management
│   │   │   ├── routes.py         # Task routes
│   │   │   └── dependencies.py   # Task dependencies
│   │   ├── analytics/            # Analytics
│   │   │   ├── routes.py         # Analytics routes
│   │   │   ├── service.py        # Analytics business logic
│   │   │   ├── repository.py     # Analytics repository
│   │   │   └── cache.py          # Analytics caching
│   │   ├── admin/                # Administrative functions
│   │   │   ├── routes.py         # Administrative routes
│   │   │   ├── dependencies.py   # Admin dependencies
│   │   │   └── create_superuser.py  # Superuser creation
│   │   └── schemas.py            # Pydantic schemas
│   ├── database/                 # Database operations
│   │   ├── db.py                 # Database connection
│   │   ├── models.py             # SQLAlchemy models
│   │   ├── migrations/           # Alembic migrations
│   │   │   └── versions/         # Migration versions
│   │   ├── populate.py           # Database test data population
│   │   └── populate_data.py      # Additional data
│   ├── infrastructure/           # Infrastructure
│   │   └── redis/                # Redis client
│   │       └── client.py         # Redis connection
│   └── tests/                    # Tests
│       ├── conftest.py           # pytest configuration
│       ├── auth/                 # Authentication tests
│       ├── task/                 # Task tests
│       └── admin/                # Admin tests
├── commands/                     # Command scripts
│   ├── create_superuser.sh       # Superuser creation
│   ├── run_migration.sh          # Run migrations
│   └── seed_data.sh              # Database data seeding
├── docker-compose.yml            # Docker Compose configuration
├── Dockerfile                    # Docker application image
├── pyproject.toml                # Project configuration and dependencies
├── alembic.ini                   # Alembic configuration
├── Makefile                      # Project management commands
├── LICENSE                       # Project license
└── README.md                     # Project documentation
```

## 🛠️ Tech Stack

### ⚡ Backend Framework
- **FastAPI** (>=0.124.4) - Modern web framework for building APIs
- **Uvicorn** (>=0.38.0) - ASGI server for running FastAPI

### 🗄️ Database
- **PostgreSQL** (17.4) - Main relational database
- **SQLAlchemy** (>=2.0.45) - ORM for database operations
- **Alembic** (>=1.17.2) - Database migrations
- **asyncpg** (>=0.31.0) - Async driver for PostgreSQL
- **aiosqlite** (>=0.22.0) - Async SQLite for testing

### ⚡ Caching
- **Redis** (7.4) - Data caching
- **redis[hiredis]** (>=7.1.0) - Python client for Redis

### 🔒 Authentication & Security
- **PyJWT** (>=2.10.1) - JWT token handling
- **Argon2-cffi** (>=25.1.0) - Password hashing
- **bcrypt** (==3.2.2) - Alternative hashing algorithm
- **passlib** (==1.7.4) - Password handling library

### ✔️ Data Validation
- **Pydantic** (>=2.12.5) - Data validation and schemas
- **Pydantic Settings** (>=2.12.0) - Settings management

### 🔧 Development Tools
- **pytest** (>=9.0.2) - Testing framework
- **pytest-cov** (>=7.0.0) - Code coverage
- **pytest-asyncio** - Async test support
- **httpx** (>=0.28.1) - HTTP client for tests
- **ruff** - Code linter and formatter
- **pre-commit** - Git hooks for code checking

### 🧰 Utilities
- **Faker** (>=39.0.0) - Test data generation
- **tqdm** (>=4.67.1) - CLI progress bars
- **python-multipart** (>=0.0.20) - Multipart form support

### 🐳 Infrastructure
- **Docker** - Application containerization
- **Docker Compose** - Container orchestration

## 📝 List of Versions

### 📌 v0.1.0 (Current Version)
- Basic task management functionality
- Authentication and authorization system
- Analytics and statistics
- Administrative functions
- Docker containerization
- Full test coverage
- Database migrations
- Redis caching

## 📄 License

This project is licensed under the MIT License.

Copyright (c) 2025 mileshkin89

Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the "Software"), to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.

The full license text is available in the [LICENSE](LICENSE) file.