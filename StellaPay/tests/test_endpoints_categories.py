import json

from django.contrib.auth.models import User
from django.http import JsonResponse
from django.test import TestCase

from StellaPay.models import Category


class TestCategories(TestCase):

    @classmethod
    def setUpTestData(cls):
        category = Category.objects.create(name="category1")
        category.save()

    def setUp(self):
        # Login test admin user
        self.user = User.objects.create_superuser(username="admin_test", email="test@admin.com",
                                                  password="test_password")

    def test_url_get_all_categories(self):
        self.client.force_login(self.user)
        response: JsonResponse = self.client.get("/categories")

        # Check if the response was correct and a JSON response
        self.assertEqual(response.status_code, 200)
        self.assertEqual(type(response), JsonResponse)

        try:
            json_data = json.loads(response.content)
        except Exception:
            self.fail("Could not parse JSON response!")

        # Check that there is at least one category in it!
        self.assertGreaterEqual(len(json_data), 1)
