from django.test import TestCase

from api.serializers.user import UserSerializer
from apps.users.models import User


class UserSerializerTest(TestCase):
    def setUp(self):
        self.user_data = {
            "username": "testuser",
            "email": "test@example.com",
            "password": "testpassword123",
            "first_name": "Test",
            "last_name": "User",
            "role": "employee",
        }
        self.user = User.objects.create_user(**self.user_data)

    def test_user_serializer_contains_expected_fields(self):
        """Тест что сериализатор содержит ожидаемые поля."""
        serializer = UserSerializer(instance=self.user)
        data = serializer.data

        # Проверяем только те поля, которые действительно есть
        expected_fields = {
            "id",
            "username",
            "email",
            "first_name",
            "last_name",
            "role",
            "date_joined",
            # Добавляем если есть в модели:
            "phone",
            "department",
            "position",
            # "is_active",  # Есть ли это поле в сериализаторе?
        }

        # Убираем поля которые могут отсутствовать
        actual_fields = set(data.keys())

        print(f"Ожидаемые поля: {expected_fields}")
        print(f"Фактические поля: {actual_fields}")

        # Проверяем что все ожидаемые поля присутствуют
        for field in expected_fields:
            self.assertIn(field, actual_fields, f"Поле '{field}' отсутствует")

    def test_user_serializer_update(self):
        """Тест обновления пользователя."""
        update_data = {
            "first_name": "Updated",
            "last_name": "Name",
            "email": "updated@example.com",
        }

        serializer = UserSerializer(self.user, data=update_data, partial=True)
        self.assertTrue(serializer.is_valid(), f"Ошибки валидации: {serializer.errors}")

        user = serializer.save()
        self.assertEqual(user.first_name, "Updated")
        self.assertEqual(user.last_name, "Name")
        self.assertEqual(user.email, "updated@example.com")

    def test_user_serializer_password_write_only(self):
        """Тест что пароль не возвращается в ответе."""
        serializer = UserSerializer(self.user)
        data = serializer.data

        self.assertNotIn("password", data)
        self.assertNotIn("password", serializer.fields)
