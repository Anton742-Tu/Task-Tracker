from django.test import TestCase
from rest_framework import status
from rest_framework.test import APIClient


class DiagnosticViewTest(TestCase):
    def setUp(self):
        self.client = APIClient()

    def test_diagnostic_endpoint_returns_200(self):
        response = self.client.get("/api/diagnostic/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_diagnostic_contains_info(self):
        response = self.client.get("/api/diagnostic/")
        self.assertIn("status", response.data)
        self.assertEqual(response.data["status"], "ok")
