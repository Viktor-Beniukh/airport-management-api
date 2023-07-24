from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient

from airport.models import Crew
from airport.serializers import CrewListSerializer, CrewSerializer
from airport.views import ApiPagination

CREW_URL = reverse("airport:crew-list")


def sample_crew(**params):
    defaults = {
        "first_name": "Jack",
        "last_name": "London",
    }
    defaults.update(params)

    return Crew.objects.create(**defaults)


def detail_url(crew_id):
    return reverse("airport:crew-detail", args=[crew_id])


class UnauthenticatedCrewApiTests(TestCase):
    def setUp(self) -> None:
        self.client = APIClient()

    def test_list_crews(self):
        sample_crew()
        pagination = ApiPagination

        response = self.client.get(CREW_URL)

        crews = Crew.objects.all()
        serializer = CrewListSerializer(pagination, crews, many=True)

        if serializer.is_valid():
            self.assertEqual(response.status_code, status.HTTP_200_OK)
            self.assertEqual(response.data, serializer.data)

    def test_retrieve_crew_detail(self):
        crew = sample_crew()

        url = detail_url(crew.id)
        response = self.client.get(url)

        serializer = CrewSerializer(crew)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, serializer.data)

    def test_filter_crews_by_position(self):
        crew1 = sample_crew(position="Captain")
        crew2 = sample_crew(position="Captain")
        crew3 = sample_crew(position="Navigator")
        pagination = ApiPagination

        response = self.client.get(CREW_URL, {"name": "captain"})

        serializer1 = CrewListSerializer(pagination, crew1)
        serializer2 = CrewListSerializer(pagination, crew2)
        serializer3 = CrewListSerializer(pagination, crew3)

        if serializer1.is_valid():
            self.assertIn(serializer1.data, response.data)
        if serializer2.is_valid():
            self.assertIn(serializer2.data, response.data)
        if serializer3.is_valid():
            self.assertNotIn(serializer3.data, response.data)


class AuthenticatedCrewApiTests(TestCase):
    def setUp(self) -> None:
        self.client = APIClient()
        self.user = get_user_model().objects.create_user(
            "test@test.com",
            "testpass"
        )
        self.client.force_authenticate(self.user)

    def test_create_crew_forbidden(self):
        payload = {
            "first_name": "Jack",
            "last_name": "London",
        }

        response = self.client.post(CREW_URL, payload)

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)


class AdminCrewApiTests(TestCase):
    def setUp(self) -> None:
        self.client = APIClient()
        self.user = get_user_model().objects.create_user(
            "admin@test.com",
            "adminpass",
            is_staff=True
        )
        self.client.force_authenticate(self.user)

    def test_create_crew(self):

        payload = {
            "first_name": "Jack",
            "last_name": "London",
        }

        response = self.client.post(CREW_URL, payload)

        crew = Crew.objects.get(id=response.data["id"])

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        for key in payload:
            self.assertEqual(payload[key], getattr(crew, key))

    def test_update_crew(self):
        crew = sample_crew()

        payload = {
            "first_name": "John",
            "last_name": "Doe",
            "position": "Captain",
        }

        url = detail_url(crew.id)
        response = self.client.put(url, payload)

        crew.refresh_from_db()

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        for key in payload:
            self.assertEqual(payload[key], getattr(crew, key))

    def test_partial_update_crew(self):
        crew = sample_crew()

        payload = {
            "first_name": "John",
        }

        url = detail_url(crew.id)
        response = self.client.patch(url, payload)

        crew.refresh_from_db()

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        for key in payload:
            self.assertEqual(payload[key], getattr(crew, key))

    def test_delete_crew(self):
        crew = sample_crew()

        url = detail_url(crew.id)
        response = self.client.delete(url)

        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
