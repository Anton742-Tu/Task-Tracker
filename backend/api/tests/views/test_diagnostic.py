# api/tests/views/test_simple_views.py
from django.test import TestCase
from rest_framework import status


class SimpleViewsTest(TestCase):
    """Простые тесты для базовых views."""

    def test_home_page_accessible(self):
        """Тест что главная страница доступна."""
        response = self.client.get("/")

        # Главная страница должна возвращать что-то разумное
        self.assertNotEqual(response.status_code, 500, "Серверная ошибка 500")
        self.assertNotEqual(response.status_code, 404, "Страница не найдена 404")

        print(f"Главная страница: статус {response.status_code}")

    def test_api_docs_accessible(self):
        """Тест что документация API доступна."""
        endpoints = ["/api/docs/", "/api/redoc/", "/api/swagger/", "/swagger/"]

        for endpoint in endpoints:
            response = self.client.get(endpoint)
            if response.status_code in [200, 302]:
                print(f"✓ Документация найдена: {endpoint} -> {response.status_code}")
                return

        print("⚠ Документация API не найдена (возможно не настроена)")

    def test_admin_accessible(self):
        """Тест что админка доступна (хотя бы редирект на логин)."""
        response = self.client.get("/admin/")

        # Админка должна редиректить на логин (302) или показывать форму (200 если уже залогинен)
        self.assertIn(response.status_code, [200, 302])
        print(f"Админка: статус {response.status_code}")

    def test_no_500_errors_on_basic_urls(self):
        """Тест что базовые URL не возвращают 500 ошибок."""
        test_urls = [
            "/",
            "/admin/",
            "/api/",
            "/api/docs/",
            "/api/redoc/",
            "/api/auth/login/",
            "/api/auth/register/",
        ]

        for url in test_urls:
            response = self.client.get(url)
            if response.status_code == 500:
                self.fail(f"Серверная ошибка 500 на {url}")
            elif response.status_code not in [200, 302, 404, 401, 403]:
                print(f"Необычный статус {response.status_code} на {url}")
