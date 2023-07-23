from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from rest_framework import status
from rest_framework.test import APIClient

from airport.models import AirplaneType


AIRPLANE_TYPE_URL = reverse("airport:airplanetype-list")


class AuthenticatedAirplaneTypeApiTests(TestCase):
    def setUp(self) -> None:
        self.client = APIClient()
        self.user = get_user_model().objects.create_user(
            "test@test.com",
            "testpass"
        )
        self.client.force_authenticate(self.user)

    def test_create_airplane_type_forbidden(self):
        payload = {
            "name": "Compact",
        }

        response = self.client.post(AIRPLANE_TYPE_URL, payload)

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)


class AdminAirplaneTypeApiTests(TestCase):
    def setUp(self) -> None:
        self.client = APIClient()
        self.user = get_user_model().objects.create_user(
            "admin@test.com",
            "adminpass",
            is_staff=True
        )
        self.client.force_authenticate(self.user)

    def test_create_airplane_type(self):

        payload = {
            "name": "Compact",
        }

        response = self.client.post(AIRPLANE_TYPE_URL, payload)

        airplane_type = AirplaneType.objects.get(id=response.data["id"])

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        for key in payload:
            self.assertEqual(payload[key], getattr(airplane_type, key))
