from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient

from airport.models import Airport
from airport.serializers import AirportSerializer
from airport.views import ApiPagination

AIRPORT_URL = reverse("airport:airport-list")


def sample_airport(**params):
    defaults = {
        "name": "Heathrow",
        "closest_big_city": "London",
    }
    defaults.update(params)

    return Airport.objects.create(**defaults)


class UnauthenticatedAirportApiTests(TestCase):
    def setUp(self) -> None:
        self.client = APIClient()

    def test_list_airports(self):
        sample_airport()
        pagination = ApiPagination

        response = self.client.get(AIRPORT_URL)

        airports = Airport.objects.all()
        serializer = AirportSerializer(pagination, airports, many=True)

        if serializer.is_valid():
            self.assertEqual(response.status_code, status.HTTP_200_OK)
            self.assertEqual(response.data, serializer.data)

    def test_filter_airports_by_name(self):
        airport1 = sample_airport(name="Heathrow")
        airport2 = sample_airport(name="Denver")
        airport3 = sample_airport(name="Indira")
        pagination = ApiPagination

        response = self.client.get(AIRPORT_URL, {"name": "denver"})

        serializer1 = AirportSerializer(pagination, airport1)
        serializer2 = AirportSerializer(pagination, airport2)
        serializer3 = AirportSerializer(pagination, airport3)

        if serializer1.is_valid():
            self.assertNotIn(serializer1.data, response.data)
        if serializer2.is_valid():
            self.assertIn(serializer2.data, response.data)
        if serializer3.is_valid():
            self.assertNotIn(serializer3.data, response.data)


class AuthenticatedAirportApiTests(TestCase):
    def setUp(self) -> None:
        self.client = APIClient()
        self.user = get_user_model().objects.create_user(
            "test@test.com",
            "testpass"
        )
        self.client.force_authenticate(self.user)

    def test_create_airport_forbidden(self):
        payload = {
            "name": "Heathrow",
            "closest_big_city": "London",
        }

        response = self.client.post(AIRPORT_URL, payload)

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)


class AdminAirportApiTests(TestCase):
    def setUp(self) -> None:
        self.client = APIClient()
        self.user = get_user_model().objects.create_user(
            "admin@test.com",
            "adminpass",
            is_staff=True
        )
        self.client.force_authenticate(self.user)

    def test_create_airport(self):
        payload = {
            "name": "Heathrow",
            "closest_big_city": "London",
        }

        response = self.client.post(AIRPORT_URL, payload)

        airport = Airport.objects.get(id=response.data["id"])

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        for key in payload:
            self.assertEqual(payload[key], getattr(airport, key))
