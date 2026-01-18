# Task Tracker - Быстрый старт

## 🚀 5-минутная настройка

1. **Клонируйте и войдите:**
```bash
git clone https://github.com/Anton742-Tu/task-tracker.git
cd task-tracker/backend
python -m venv .venv
.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```
2. **Настройте окружение:**

```bash
copy .env.example .env
# Отредактируйте .env - оставьте значения по умолчанию для разработки
```
3. **Запустите базу и сервер:**

```bash
python manage.py migrate
python manage.py createsuperuser
$env:DJANGO_ENVIRONMENT='development'
python manage.py runserver
```
4. **Откройте в браузере:**

http://localhost:8000/ - главная

http://localhost:8000/admin/ - админка

http://localhost:8000/swagger/ - документация API

## 🔧 Если что-то не работает
### Ошибка 400 Bad Request
```bash
echo "ALLOWED_HOSTS=*" >> .env
echo "SECRET_KEY=dev-key-123" >> .env
$env:DJANGO_ENVIRONMENT='development'
```
### Ошибки тестов
```bash
$env:PYTHONUTF8='1'
pytest --disable-warnings
```
### Проблемы с базой данных
```bash
# Используйте SQLite для простоты
echo "DB_ENGINE=django.db.backends.sqlite3" >> .env
python manage.py migrate
```
## 📞 Быстрая помощь
- Проверьте что .env файл существует
- Убедитесь что DJANGO_ENVIRONMENT=development
- Перезапустите сервер после изменений .env
