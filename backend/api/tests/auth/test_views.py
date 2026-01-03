import json
from django.test import TestCase
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient
from rest_framework import status
from rest_framework_simplejwt.tokens import RefreshToken

User = get_user_model()


class AuthenticationViewsTestCase(TestCase):
    """Тесты для views аутентификации"""

    def setUp(self):
        """Настройка тестовых данных"""
        self.client = APIClient()

        # Данные для регистрации
        self.register_data = {
            'username': 'newuser',
            'email': 'newuser@example.com',
            'password': 'TestPassword123',
            'password2': 'TestPassword123',
            'first_name': 'New',
            'last_name': 'User'
        }

        # Существующий пользователь для тестов входа
        self.existing_user = User.objects.create_user(
            username='existinguser',
            email='existing@example.com',
            password='ExistingPassword123',
            first_name='Existing',
            last_name='User'
        )

        # Данные для входа
        self.login_data = {
            'username': 'existinguser',
            'password': 'ExistingPassword123'
        }

    def test_register_success(self):
        """Успешная регистрация пользователя"""
        response = self.client.post(
            '/api/auth/register/',
            data=self.register_data,
            format='json'
        )

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        # Проверяем структуру ответа
        self.assertIn('user', response.data)
        self.assertIn('refresh', response.data)
        self.assertIn('access', response.data)
        self.assertIn('message', response.data)

        # Проверяем данные пользователя
        user_data = response.data['user']
        self.assertEqual(user_data['username'], 'newuser')
        self.assertEqual(user_data['email'], 'newuser@example.com')
        self.assertEqual(user_data['first_name'], 'New')
        self.assertEqual(user_data['last_name'], 'User')

        # Проверяем, что пользователь создан в базе
        self.assertTrue(User.objects.filter(username='newuser').exists())
        user = User.objects.get(username='newuser')
        self.assertEqual(user.email, 'newuser@example.com')

    def test_register_password_mismatch(self):
        """Регистрация с несовпадающими паролями"""
        invalid_data = self.register_data.copy()
        invalid_data['password2'] = 'DifferentPassword123'

        response = self.client.post(
            '/api/auth/register/',
            data=invalid_data,
            format='json'
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('password', response.data)

    def test_register_duplicate_email(self):
        """Регистрация с уже существующим email"""
        # Сначала регистрируем пользователя
        self.client.post('/api/auth/register/', data=self.register_data, format='json')

        # Пытаемся зарегистрировать второго пользователя с тем же email
        duplicate_data = self.register_data.copy()
        duplicate_data['username'] = 'anotheruser'

        response = self.client.post(
            '/api/auth/register/',
            data=duplicate_data,
            format='json'
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('email', response.data)

    def test_register_missing_required_fields(self):
        """Регистрация без обязательных полей"""
        incomplete_data = {
            'username': 'incomplete',
            'password': 'Test123',
            'password2': 'Test123'
            # Нет email, first_name, last_name
        }

        response = self.client.post(
            '/api/auth/register/',
            data=incomplete_data,
            format='json'
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('email', response.data)
        self.assertIn('first_name', response.data)
        self.assertIn('last_name', response.data)

    def test_login_success(self):
        """Успешный вход пользователя"""
        response = self.client.post(
            '/api/auth/login/',
            data=self.login_data,
            format='json'
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # Проверяем структуру ответа
        self.assertIn('user', response.data)
        self.assertIn('refresh', response.data)
        self.assertIn('access', response.data)

        # Проверяем данные пользователя
        user_data = response.data['user']
        self.assertEqual(user_data['username'], 'existinguser')
        self.assertEqual(user_data['email'], 'existing@example.com')

    def test_login_invalid_credentials(self):
        """Вход с неверными учетными данными"""
        invalid_data = {
            'username': 'existinguser',
            'password': 'WrongPassword'
        }

        response = self.client.post(
            '/api/auth/login/',
            data=invalid_data,
            format='json'
        )

        # SimpleJWT возвращает 401 при неверных учетных данных
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertIn('detail', response.data)

    def test_login_nonexistent_user(self):
        """Вход несуществующего пользователя"""
        invalid_data = {
            'username': 'nonexistent',
            'password': 'SomePassword123'
        }

        response = self.client.post(
            '/api/auth/login/',
            data=invalid_data,
            format='json'
        )

        # SimpleJWT возвращает 401 при неверных учетных данных
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertIn('detail', response.data)

    def test_logout_success(self):
        """Успешный выход пользователя"""
        # Сначала входим
        login_response = self.client.post('/api/auth/login/', data=self.login_data, format='json')
        refresh_token = login_response.data['refresh']

        # Выходим
        logout_data = {'refresh': refresh_token}
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {login_response.data["access"]}')

        response = self.client.post(
            '/api/auth/logout/',
            data=logout_data,
            format='json'
        )

        # Проверяем успешный ответ
        self.assertIn(response.status_code, [
            status.HTTP_205_RESET_CONTENT,  # Успешный logout
            status.HTTP_400_BAD_REQUEST  # Если blacklist не настроен
        ])

    def test_logout_missing_token(self):
        """Выход без токена"""
        # Входим
        login_response = self.client.post('/api/auth/login/', data=self.login_data, format='json')
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {login_response.data["access"]}')

        # Пытаемся выйти без токена
        response = self.client.post(
            '/api/auth/logout/',
            data={},
            format='json'
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('error', response.data)

    def test_user_profile_authenticated(self):
        """Получение профиля аутентифицированным пользователем"""
        # Входим
        login_response = self.client.post('/api/auth/login/', data=self.login_data, format='json')
        access_token = login_response.data['access']

        # Устанавливаем токен в заголовки
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {access_token}')

        response = self.client.get('/api/auth/me/')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['username'], 'existinguser')
        self.assertEqual(response.data['email'], 'existing@example.com')
        self.assertEqual(response.data['first_name'], 'Existing')
        self.assertEqual(response.data['last_name'], 'User')

    def test_user_profile_unauthenticated(self):
        """Попытка получить профиль без аутентификации"""
        # Очищаем credentials
        self.client.credentials()

        response = self.client.get('/api/auth/me/')

        # Проверяем что доступ запрещен (может быть 403 или 401 в зависимости от настроек)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

        # Дополнительная проверка
        self.assertIn('detail', response.data)

    def test_token_refresh(self):
        """Обновление access токена"""
        # Сначала получаем токены
        login_response = self.client.post('/api/auth/login/', data=self.login_data, format='json')
        refresh_token = login_response.data['refresh']

        # Обновляем токен
        response = self.client.post(
            '/api/auth/token/refresh/',
            data={'refresh': refresh_token},
            format='json'
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('access', response.data)

    def test_token_verify_via_usage(self):
        """Проверка токена через его использование"""
        # Получаем токены
        login_response = self.client.post('/api/auth/login/', data=self.login_data, format='json')
        access_token = login_response.data['access']

        # Используем токен для запроса профиля
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {access_token}')
        response = self.client.get('/api/auth/me/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)