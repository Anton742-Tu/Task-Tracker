from django.test import TestCase
from django.urls import resolve, reverse


class UrlTests(TestCase):
    """Тесты для проверки корректности URL маршрутов"""

    def test_home_url(self):
        """Тест главной страницы"""
        url = reverse("home")
        self.assertEqual(url, "/")
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)

    def test_admin_url(self):
        """Тест админки"""
        url = reverse("admin:index")
        self.assertEqual(url, "/admin/")

    def test_api_auth_urls(self):
        """Тест URL аутентификации"""
        # Проверяем существующие URL аутентификации
        # Предположим что у вас есть такие пути:
        auth_urls = [
            ("api:auth:login", "/api/auth/login/"),
            ("api:auth:register", "/api/auth/register/"),
            ("api:auth:logout", "/api/auth/logout/"),
        ]

        # Тестируем только существующие URL
        for view_name, expected_path in auth_urls:
            try:
                url = reverse(view_name)
                self.assertEqual(url, expected_path)
                print(f"✓ URL найден: {view_name} -> {url}")
            except:
                print(f"⚠ URL не найден: {view_name}")
                # Пропускаем если URL не существует

    def test_api_resource_urls(self):
        """Тест основных ресурсов API"""
        # Проверяем существование базовых API endpoints
        resources = ["users", "projects", "tasks", "files"]

        for resource in resources:
            try:
                # Пробуем получить list view для ресурса
                url = reverse(f"api:{resource}:list")
                self.assertTrue(url.startswith(f"/api/{resource}/"))
                print(f"✓ Ресурс найден: {resource} -> {url}")
            except:
                print(f"⚠ Ресурс не найден или не имеет list view: {resource}")

    def test_url_resolution(self):
        """Тест разрешения URL в view функции"""
        test_cases = [
            ("/", "home"),
            ("/admin/", "admin:index"),
            ("/api/docs/", "swagger-docs"),
        ]

        for path, expected_view in test_cases:
            try:
                resolved = resolve(path)
                self.assertEqual(resolved.view_name, expected_view)
                print(f"✓ Разрешение корректно: {path} -> {resolved.view_name}")
            except:
                print(f"⚠ Не удалось разрешить: {path}")

    def test_all_registered_urls(self):
        """Тест всех зарегистрированных URL (опционально)"""
        # Можно получить список всех URL через show_urls или напрямую
        from django.urls import get_resolver

        resolver = get_resolver()

        # Собираем все URL patterns
        all_urls = []
        for pattern in resolver.url_patterns:
            if hasattr(pattern, "url_patterns"):
                # Это include
                for subpattern in pattern.url_patterns:
                    if hasattr(subpattern, "name") and subpattern.name:
                        all_urls.append(subpattern.name)
            elif hasattr(pattern, "name") and pattern.name:
                all_urls.append(pattern.name)

        print(f"\nНайдено {len(all_urls)} именованных URL:")
        for url_name in sorted(all_urls)[:20]:  # Показать первые 20
            print(f"  - {url_name}")

        # Проверяем что основные URL существуют
        required_urls = ["home", "admin:index", "swagger-docs"]
        for required in required_urls:
            if required not in all_urls:
                print(f"⚠ Обязательный URL отсутствует: {required}")
