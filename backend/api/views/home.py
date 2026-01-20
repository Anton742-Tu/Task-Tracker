from django.shortcuts import render
from django.utils import timezone
import django
import sys
from django.db import connection


def home_view(request):
    """Заглушка - перенаправление на реальный view"""
    # Просто редирект или импорт из urls.py
    from config.urls import home_view as real_home_view

    return real_home_view(request)
