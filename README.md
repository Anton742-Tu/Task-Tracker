@"
# Task Tracker - Система управления задачами сотрудников

Проект дипломной работы: Трекер задач сотрудников.

## 🚀 Технологический стек

### Backend
- **Python 3.12** - Основной язык программирования
- **Django 5.0** - Веб-фреймворк
- **Django REST Framework** - API фреймворк
- **PostgreSQL** - База данных
- **Docker & Docker Compose** - Контейнеризация

### Инструменты разработки
- **Poetry** - Управление зависимостями
- **Black, Flake8** - Форматирование и линтинг
- **Pytest** - Тестирование
- **Git** - Контроль версий

## 📦 Установка и запуск

### 1. Клонирование репозитория
```bash
git clone <repository-url>
cd Task-Tracker
2. Настройка виртуального окружения
bash
cd backend
python -m venv .venv

# Windows PowerShell
.\.venv\Scripts\Activate.ps1

# Windows CMD
.venv\Scripts\activate.bat

# Linux/Mac
source .venv/bin/activate
3. Установка зависимостей
bash
pip install -r requirements.txt
4. Настройка переменных окружения
bash
cp .env.example .env
# Отредактируйте .env файл под свои настройки
5. Запуск PostgreSQL через Docker
bash
docker-compose up -d postgres
6. Миграции базы данных
bash
python manage.py migrate
python manage.py createsuperuser
7. Запуск сервера разработки
bash
python manage.py runserver
🌐 Доступ к сервисам
Django сервер: http://localhost:8000

Админ-панель: http://localhost:8000/admin

API документация (Swagger): http://localhost:8000/swagger

pgAdmin (управление БД): http://localhost:5050

Email: admin@admin.com

Password: admin

📁 Структура проекта
text
Task-Tracker/
├── backend/                 # Django бэкенд
│   ├── apps/               # Приложения Django
│   │   ├── users/         # Пользователи и аутентификация
│   │   ├── projects/      # Проекты
│   │   ├── tasks/         # Задачи
│   │   └── notifications/ # Уведомления
│   ├── config/            # Настройки Django
│   ├── .env              # Переменные окружения
│   ├── requirements.txt  # Зависимости Python
│   └── manage.py         # Django CLI
├── docker-compose.yml    # Docker конфигурация
└── README.md            # Документация
🔧 Команды разработки
bash
# Запуск тестов
pytest

# Проверка стиля кода
black .
flake8

# Создание миграций
python manage.py makemigrations

# Применение миграций
python manage.py migrate

# Создание суперпользователя
python manage.py createsuperuser
📝 Лицензия
Проект создан для дипломной работы.
"@ | Out-File -FilePath "README.md" -Encoding UTF8

text

## **Шаг 7: Подготавливаем первый коммит**

```powershell
# Инициализируем git в корне проекта
cd C:\Users\Tumas_c7ctj2q\PycharmProjects\Task-Tracker
git init

# Добавляем .gitignore в корень
@"
# Python
__pycache__/
*.py[cod]
*$py.class
*.so
.Python
build/
develop-eggs/
dist/
downloads/
eggs/
.eggs/
lib/
lib64/
parts/
sdist/
var/
wheels/
*.egg-info/
.installed.cfg
*.egg
MANIFEST

# Virtual environments
backend/.venv/
venv/
env/
ENV/
env.bak/
venv.bak/

# IDE
.vscode/
.idea/
*.swp
*.swo

# OS
.DS_Store
.DS_Store?
._*
.Spotlight-V100
.Trashes
ehthumbs.db
Thumbs.db

# Docker
docker-data/

# Django
*.log
*.pot
*.pyc
db.sqlite3
media/
staticfiles/

# Environment variables
.env
!/.env.example

# Database dumps
*.dump
*.sql

# Logs
*.log
"@ | Out-File -FilePath ".gitignore" -Encoding UTF8

# Добавляем файлы в git
git add .

# Проверяем, что будет добавлено
git status

# Делаем первый коммит
git commit -m "Initial commit: Django project setup with PostgreSQL"

# Если нужно добавить удаленный репозиторий
# git remote add origin <your-repository-url>
# git branch -M main
# git push -u origin main
Шаг 8: Проверяем работоспособность
powershell
# Запускаем все сервисы
docker-compose up -d

# Переходим в backend
cd backend

# Активируем окружение
.\.venv\Scripts\Activate.ps1

# Проверяем соединение с БД
python manage.py check --database default

# Запускаем сервер
python manage.py runserver
Что мы сделали:
✅ Настроили PostgreSQL через Docker

✅ Добавили переменные окружения (.env, .env.example)

✅ Обновили settings.py для работы с PostgreSQL

✅ Создали docker-compose.yml с PostgreSQL и pgAdmin

✅ Создали README.md с документацией

✅ Подготовили проект к первому коммиту

Для проверки:
Откройте http://localhost:8000/admin/ - должна загрузиться админка

Откройте http://localhost:5050 - pgAdmin для управления БД

В pgAdmin подключитесь к серверу:

Host: postgres (или localhost)

Port: 5432

Username: postgres

Password: postgres