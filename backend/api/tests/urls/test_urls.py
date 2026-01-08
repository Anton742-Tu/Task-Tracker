from django.test import TestCase
from django.urls import resolve, reverse


class UrlTests(TestCase):
    def test_home_url(self):
        url = reverse("home")
        self.assertEqual(resolve(url).view_name, "home")

    def test_api_root(self):
        url = reverse("api-root")
        self.assertEqual(resolve(url).view_name, "api-root")

    def test_auth_urls(self):
        urls_to_test = [
            ("login", "rest_login"),
            ("logout", "rest_logout"),
            ("register", "rest_register"),
        ]
        for name, view_name in urls_to_test:
            url = reverse(f"rest_{name}")
            self.assertEqual(resolve(url).view_name, view_name)
