from django.contrib.auth import get_user_model
from django.test import TestCase

from api.serializers.auth import RegisterSerializer, UserSerializer

User = get_user_model()


class AuthSerializersTestCase(TestCase):
    """Тесты для сериализаторов аутентификации"""

    def setUp(self):
        """Настройка тестовых данных"""
        self.user_data = {
            "username": "testuser",
            "email": "test@example.com",
            "password": "TestPassword123",
            "password2": "TestPassword123",
            "first_name": "Test",
            "last_name": "User",
        }

        self.existing_user = User.objects.create_user(
            username="existing",
            email="existing@example.com",
            password="ExistingPassword123",
            first_name="Existing",
            last_name="User",
        )

    def test_register_serializer_valid(self):
        """Валидные данные для регистрации"""
        serializer = RegisterSerializer(data=self.user_data)

        self.assertTrue(serializer.is_valid())

        # Проверяем создание пользователя
        user = serializer.save()
        self.assertEqual(user.username, "testuser")
        self.assertEqual(user.email, "test@example.com")
        self.assertEqual(user.first_name, "Test")
        self.assertEqual(user.last_name, "User")

        # Проверяем, что пароль установлен
        self.assertTrue(user.check_password("TestPassword123"))

    def test_register_serializer_password_mismatch(self):
        """Несовпадающие пароли"""
        invalid_data = self.user_data.copy()
        invalid_data["password2"] = "DifferentPassword123"

        serializer = RegisterSerializer(data=invalid_data)

        self.assertFalse(serializer.is_valid())
        self.assertIn("password", serializer.errors)

    def test_register_serializer_duplicate_email(self):
        """Дублирующийся email"""
        # Меняем username, оставляем тот же email
        duplicate_data = self.user_data.copy()
        duplicate_data["username"] = "differentuser"
        duplicate_data["email"] = "existing@example.com"  # Существующий email

        serializer = RegisterSerializer(data=duplicate_data)

        self.assertFalse(serializer.is_valid())
        self.assertIn("email", serializer.errors)

    def test_register_serializer_weak_password(self):
        """Слишком слабый пароль"""
        weak_password_data = self.user_data.copy()
        weak_password_data["password"] = "123"  # Слишком короткий
        weak_password_data["password2"] = "123"

        serializer = RegisterSerializer(data=weak_password_data)

        self.assertFalse(serializer.is_valid())
        self.assertIn("password", serializer.errors)

    def test_user_serializer(self):
        """Сериализатор пользователя"""
        serializer = UserSerializer(self.existing_user)
        data = serializer.data

        self.assertEqual(data["username"], "existing")
        self.assertEqual(data["email"], "existing@example.com")
        self.assertEqual(data["first_name"], "Existing")
        self.assertEqual(data["last_name"], "User")
        self.assertIn("role_display", data)
        self.assertIn("date_joined", data)
        self.assertIn("last_login", data)
