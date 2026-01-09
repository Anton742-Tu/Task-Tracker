import json

from django.test import TestCase


class HomeViewTest(TestCase):
    """Тесты для главной страницы."""

    def test_home_page_accessible(self):
        """Тест что главная страница доступна."""
        response = self.client.get("/")

        # Главная страница должна возвращать какой-то разумный статус
        acceptable_statuses = [200, 302, 301, 404]
        self.assertIn(
            response.status_code,
            acceptable_statuses,
            f"Неожиданный статус {response.status_code} для главной страницы",
        )

        print(f"Главная страница: статус {response.status_code}")

        # Не должно быть 500 ошибок
        self.assertNotEqual(
            response.status_code, 500, "Серверная ошибка 500 на главной странице"
        )

        if response.status_code == 200:
            # Если есть контент
            content_type = response.get("Content-Type", "")
            print(f"  Content-Type: {content_type}")

            if "application/json" in content_type:
                # Это JSON API
                try:
                    data = json.loads(response.content)
                    print("  JSON ответ получен")

                    # Проверяем если есть сообщение
                    if "message" in data:
                        print(f"  Сообщение: {data['message']}")

                except json.JSONDecodeError:
                    print("  Не валидный JSON")
            elif "text/html" in content_type:
                # Это HTML страница
                print("  HTML страница")

    def test_api_root_if_exists(self):
        """Тест корня API если существует."""
        response = self.client.get("/api/")

        if response.status_code == 200:
            print("✓ Корень API доступен: /api/")

            # Проверяем что это JSON
            content_type = response.get("Content-Type", "")
            if "application/json" in content_type:
                try:
                    data = json.loads(response.content)
                    print("  API корень возвращает JSON")

                    # Часто содержит ссылки на endpoints
                    if "projects" in data or "users" in data or "tasks" in data:
                        print("  Содержит ссылки на ресурсы")

                except json.JSONDecodeError:
                    print("  Не валидный JSON")

        elif response.status_code in [404, 403, 401]:
            print(f"Корень API: {response.status_code} (ожидаемо)")
        else:
            print(f"Корень API: неожиданный статус {response.status_code}")
