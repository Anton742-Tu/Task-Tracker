class HomeViewTest(TestCase):
    def test_home_page(self):
        response = self.client.get("/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("API", response.data.get("message", ""))
