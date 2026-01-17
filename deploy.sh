#!/bin/bash

# Pull latest changes
git pull origin main

# Update dependencies if needed
cd backend
pip install -r requirements.txt

# Run migrations
python manage.py migrate

# Collect static files
python manage.py collectstatic --noinput

# Restart services
sudo systemctl restart gunicorn
sudo systemctl restart nginx

echo "Deployment completed!"
