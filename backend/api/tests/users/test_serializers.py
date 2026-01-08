from django.test import TestCase

from api.serializers.user import UserSerializer
from apps.users.models import User


class UserSerializerTest(TestCase):
    def setUp(self):
        self.user_data = {
            "username": "testuser",
            "email": "test@example.com",
            "first_name": "Test",
            "last_name": "User",
            "role": "employee",
        }
        self.user = User.objects.create_user(**self.user_data)

    def test_user_serializer_contains_expected_fields(self):
        serializer = UserSerializer(instance=self.user)
        data = serializer.data
        self.assertEqual(
            set(data.keys()),
            {
                "id",
                "username",
                "email",
                "first_name",
                "last_name",
                "role",
                "is_active",
                "date_joined",
            },
        )

    def test_user_serializer_create(self):
        new_data = {
            "username": "newuser",
            "email": "new@example.com",
            "password": "password123",
            "role": "employee",
        }
        serializer = UserSerializer(data=new_data)
        self.assertTrue(serializer.is_valid())
        user = serializer.save()
        self.assertEqual(user.username, "newuser")
