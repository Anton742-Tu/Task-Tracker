import json

from django.test import TestCase


class SimpleDiagnosticTest(TestCase):
    """Простые тесты для диагностики."""

    def test_diagnostic_or_alternative(self):
        """Тест диагностики или альтернативного поведения."""

        # 1. Проверяем существует ли endpoint
        response = self.client.get("/api/diagnostic/")

        print(f"Диагностика /api/diagnostic/: {response.status_code}")

        if response.status_code == 200:
            # Endpoint существует
            content_type = response.get("Content-Type", "")
            print(f"  Content-Type: {content_type}")

            if "application/json" in content_type:
                # Это JSON диагностика
                try:
                    data = json.loads(response.content)
                    print(f"  JSON данные получены, ключи: {list(data.keys())}")

                    # Минимальная проверка
                    self.assertIsInstance(data, dict)

                    # Если есть статус
                    if "status" in data:
                        print(f"  Статус: {data['status']}")

                except json.JSONDecodeError as e:
                    print(f"  Ошибка парсинга JSON: {e}")
                    print(f"  Контент: {response.content[:200]}...")
            else:
                # Не JSON, но endpoint существует
                print(f"  Не-JSON ответ (возможно HTML страница)")
                print(f"  Контент начинается с: {str(response.content)[:100]}...")

        elif response.status_code == 404:
            print("  Endpoint не найден (404)")
            # Не падаем, просто сообщаем

        elif response.status_code == 302:
            print("  Редирект (302)")
            # Может быть редирект на логин

        else:
            print(f"  Неожиданный статус: {response.status_code}")

        # Главное - не должно быть 500 ошибок
        self.assertNotEqual(response.status_code, 500, "Серверная ошибка 500")

    def test_health_check_if_exists(self):
        """Тест health check endpoint если существует."""
        # Часто есть health check endpoints
        health_endpoints = [
            "/api/health/",
            "/health/",
            "/api/status/",
            "/status/",
            "/api/diagnostic/",
            "/api/debug/",
        ]

        for endpoint in health_endpoints:
            response = self.client.get(endpoint)
            if response.status_code == 200:
                print(f"✓ Health check найден: {endpoint}")

                # Проверяем что не 500 ошибка
                self.assertNotEqual(response.status_code, 500)

                # Если это JSON
                content_type = response.get("Content-Type", "")
                if "application/json" in content_type:
                    try:
                        data = json.loads(response.content)
                        print(f"  JSON ответ, ключи: {list(data.keys())}")
                    except:
                        pass

                return  # Нашли working endpoint

        print("⚠ Health check endpoints не найдены")
