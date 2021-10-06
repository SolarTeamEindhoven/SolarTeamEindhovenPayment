import json

from django.contrib.auth.models import User
from django.http import JsonResponse
from django.test import TestCase
from django.urls import reverse

from StellaPay.models import RegistrationDevice, Customer


class TestIdentification(TestCase):

    @classmethod
    def setUpTestData(cls):

        customer = Customer.objects.create(first_name="test", last_name="name", email="test@test.com")
        customer.save()

        number_of_cards = 10

        for i in range(0, number_of_cards):
            card = RegistrationDevice.objects.create(uuid=str(i), owner=customer)
            card.save()

    def setUp(self):
        # Login test admin user
        self.user = User.objects.create_superuser(username="admin_test", email="test@admin.com",
                                                  password="test_password")

    def test_url_get_all_cards(self):
        self.client.force_login(self.user)
        response: JsonResponse = self.client.get(reverse("retrieve-all-cards"))

        # Check if the response was correct and a JSON response
        self.assertEqual(response.status_code, 200)
        self.assertEqual(type(response), JsonResponse)

        try:
            json_data = json.loads(response.content)
        except Exception:
            self.fail("Could not parse JSON response!")

        # Check that there is at least one category in it!
        self.assertGreaterEqual(len(json_data), 10)
