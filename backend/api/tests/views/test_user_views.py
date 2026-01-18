# -*- coding: utf-8 -*-
from django.test import TestCase
from rest_framework import status
from rest_framework.test import APIClient

from apps.users.models import User


class UserViewSetTest(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.admin = User.objects.create_user(
            username="admin",
            email="admin@test.com",
            password="password123",
            role="admin",
        )
        self.user = User.objects.create_user(
            username="user",
            email="user@test.com",
            password="password123",
            role="employee",
        )

    def test_user_list_as_admin(self):
        self.client.force_authenticate(user=self.admin)
        response = self.client.get("/api/users/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
