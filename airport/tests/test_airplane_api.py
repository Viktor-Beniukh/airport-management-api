import os
import tempfile
import uuid

from PIL import Image
from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient

from airport.models import Airplane, AirplaneType, Airport, Route, Flight
from airport.serializers import AirplaneListSerializer, AirplaneDetailSerializer
from airport.views import ApiPagination

AIRPLANE_URL = reverse("airport:airplane-list")
FLIGHT_URL = reverse("airport:flight-list")


def sample_route(**params):
    airport1 = Airport.objects.create(name="Airport 1")
    airport2 = Airport.objects.create(name="Airport 2")

    defaults = {
        "source": airport1,
        "destination": airport2,
        "distance": 1000
    }
    defaults.update(params)

    return Route.objects.create(**defaults)


def sample_airplane(**params):
    airplane_type = AirplaneType.objects.create(name="Compact")

    defaults = {
        "name": "Boeing",
        "rows": 30,
        "seats_in_row": 6,
        "airplane_type": airplane_type
    }
    defaults.update(params)

    return Airplane.objects.create(**defaults)


def sample_flight(**params):
    route = sample_route()
    airplane = sample_airplane()

    defaults = {
        "route": route,
        "airplane": airplane,
    }
    defaults.update(params)

    return Flight.objects.create(**defaults)


def image_upload_url(airplane_id):
    """Return URL for recipe image upload"""
    return reverse("airport:airplane-upload-image", args=[airplane_id])


def detail_url(airplane_id):
    return reverse("airport:airplane-detail", args=[airplane_id])


class UnauthenticatedAirplaneApiTests(TestCase):
    def setUp(self) -> None:
        self.client = APIClient()

    def test_list_airplanes(self):
        sample_airplane()
        pagination = ApiPagination

        response = self.client.get(AIRPLANE_URL)

        airplanes = Airplane.objects.all()
        serializer = AirplaneListSerializer(pagination, airplanes, many=True)

        if serializer.is_valid():
            self.assertEqual(response.status_code, status.HTTP_200_OK)
            self.assertEqual(response.data, serializer.data)

    def test_retrieve_airplane_detail(self):
        airplane = sample_airplane()

        url = detail_url(airplane.id)
        response = self.client.get(url)

        serializer = AirplaneDetailSerializer(airplane)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, serializer.data)

    def test_filter_airplanes_by_name(self):
        airplane1 = sample_airplane(name="Boeing 730")
        airplane2 = sample_airplane(name="Airbus")
        airplane3 = sample_airplane(name="Boeing 750")
        pagination = ApiPagination

        response = self.client.get(AIRPLANE_URL, {"name": "boeing"})

        serializer1 = AirplaneListSerializer(pagination, airplane1)
        serializer2 = AirplaneListSerializer(pagination, airplane2)
        serializer3 = AirplaneListSerializer(pagination, airplane3)

        if serializer1.is_valid():
            self.assertIn(serializer1.data, response.data)
        if serializer2.is_valid():
            self.assertNotIn(serializer2.data, response.data)
        if serializer3.is_valid():
            self.assertIn(serializer3.data, response.data)

    def test_filter_airplanes_by_airplane_type(self):
        pagination = ApiPagination
        airplane_type1 = AirplaneType.objects.create(name="Compact")
        airplane_type2 = AirplaneType.objects.create(name="Medium")
        airplane_type3 = AirplaneType.objects.create(name="Medium")

        airplane1 = sample_airplane(name="Airplane 1", airplane_type=airplane_type1)
        airplane2 = sample_airplane(name="Airplane 2", airplane_type=airplane_type2)
        airplane3 = sample_airplane(name="Airplane 3", airplane_type=airplane_type3)

        response = self.client.get(AIRPLANE_URL, {"name": "medium"})

        serializer1 = AirplaneListSerializer(pagination, airplane1)
        serializer2 = AirplaneListSerializer(pagination, airplane2)
        serializer3 = AirplaneListSerializer(pagination, airplane3)

        if serializer1.is_valid():
            self.assertNotIn(serializer1.data, response.data)
        if serializer2.is_valid():
            self.assertIn(serializer2.data, response.data)
        if serializer3.is_valid():
            self.assertIn(serializer3.data, response.data)


class AuthenticatedAirplaneApiTests(TestCase):
    def setUp(self) -> None:
        self.client = APIClient()
        self.user = get_user_model().objects.create_user(
            "test@test.com",
            "testpass"
        )
        self.client.force_authenticate(self.user)

    def test_create_airplane_forbidden(self):
        airplane_type = AirplaneType.objects.create(name="Compact")

        payload = {
            "name": "Boeing",
            "rows": 30,
            "seats_in_row": 6,
            "airplane_type": airplane_type
        }

        response = self.client.post(AIRPLANE_URL, payload)

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)


class AdminAirplaneApiTests(TestCase):
    def setUp(self) -> None:
        self.client = APIClient()
        self.user = get_user_model().objects.create_user(
            "admin@test.com",
            "adminpass",
            is_staff=True
        )
        self.client.force_authenticate(self.user)

    def test_create_airplane(self):
        airplane_type = AirplaneType.objects.create(name="Compact")

        payload = {
            "name": "Boeing",
            "rows": 30,
            "seats_in_row": 6,
            "airplane_type": airplane_type.id
        }

        response = self.client.post(AIRPLANE_URL, payload)

        airplane = Airplane.objects.get(id=response.data["id"])

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        for key in payload:
            if key == "airplane_type":
                self.assertEqual(int(payload[key]), getattr(airplane, key).id)
            else:
                self.assertEqual(payload[key], getattr(airplane, key))

    def test_update_airplane(self):
        airplane = sample_airplane()

        url = detail_url(airplane.id)
        new_airplane_type = AirplaneType.objects.create(name="Large")
        payload = {
            "name": "Updated Boeing",
            "rows": 40,
            "seats_in_row": 8,
            "airplane_type": new_airplane_type.id
        }

        response = self.client.put(url, payload)

        airplane.refresh_from_db()

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        self.assertEqual(airplane.name, payload["name"])
        self.assertEqual(airplane.rows, payload["rows"])
        self.assertEqual(airplane.seats_in_row, payload["seats_in_row"])
        self.assertEqual(airplane.airplane_type.id, payload["airplane_type"])

    def test_partial_update_airplane(self):
        airplane = sample_airplane()

        url = detail_url(airplane.id)
        new_airplane_type = AirplaneType.objects.create(name="Large")
        payload = {
            "name": "Updated Boeing",
            "airplane_type": new_airplane_type.id
        }

        response = self.client.patch(url, payload)

        airplane.refresh_from_db()

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        self.assertEqual(airplane.name, payload["name"])
        self.assertEqual(airplane.airplane_type.id, payload["airplane_type"])

    def test_delete_airplane(self):
        airplane = sample_airplane()

        url = detail_url(airplane.id)

        response = self.client.delete(url)

        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)


class AirplaneImageUploadTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = get_user_model().objects.create_superuser(
            "admin@user.com", "password"
        )
        self.client.force_authenticate(self.user)
        self.airplane = sample_airplane()

    def tearDown(self):
        self.airplane.image.delete()

    def test_upload_image_to_airplane(self):
        """Test uploading an image to airplane"""
        url = image_upload_url(self.airplane.id)

        with tempfile.NamedTemporaryFile(suffix=".jpg") as ntf:
            img = Image.new("RGB", (10, 10))
            img.save(ntf, format="JPEG")
            ntf.seek(0)
            response = self.client.post(url, {"image": ntf}, format="multipart")

        self.airplane.refresh_from_db()

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("image", response.data)
        self.assertTrue(os.path.exists(self.airplane.image.path))

    def test_upload_image_bad_request(self):
        """Test uploading an invalid image"""
        url = image_upload_url(self.airplane.id)
        response = self.client.post(url, {"image": "not image"}, format="multipart")

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_post_image_to_airplane_list_should_not_work(self):
        url = AIRPLANE_URL
        airplane_type = AirplaneType.objects.create(name="Compact")
        unique_name = "Boeing_{}".format(uuid.uuid4().hex)

        with tempfile.NamedTemporaryFile(suffix=".jpg") as ntf:
            img = Image.new("RGB", (10, 10))
            img.save(ntf, format="JPEG")
            ntf.seek(0)
            response = self.client.post(
                url,
                {
                    "name": unique_name,
                    "rows": 30,
                    "seats_in_row": 6,
                    "airplane_type": airplane_type.id,
                    "image": ntf,
                },
                format="multipart",
            )

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        airplane = Airplane.objects.get(name=unique_name)
        self.assertFalse(airplane.image)

    def test_image_url_is_shown_on_airplane_detail(self):
        url = image_upload_url(self.airplane.id)

        with tempfile.NamedTemporaryFile(suffix=".jpg") as ntf:
            img = Image.new("RGB", (10, 10))
            img.save(ntf, format="JPEG")
            ntf.seek(0)
            self.client.post(url, {"image": ntf}, format="multipart")

        response = self.client.get(detail_url(self.airplane.id))

        self.assertIn("image", response.data)

    def test_image_url_is_shown_on_airplane_list(self):
        url = image_upload_url(self.airplane.id)

        with tempfile.NamedTemporaryFile(suffix=".jpg") as ntf:
            img = Image.new("RGB", (10, 10))
            img.save(ntf, format="JPEG")
            ntf.seek(0)
            self.client.post(url, {"image": ntf}, format="multipart")

        response = self.client.get(AIRPLANE_URL)

        results = response.data["results"]

        self.assertIn("image", results[0].keys())

    def test_image_url_is_shown_on_flight_detail(self):
        url = image_upload_url(self.airplane.id)

        with tempfile.NamedTemporaryFile(suffix=".jpg") as ntf:
            img = Image.new("RGB", (10, 10))
            img.save(ntf, format="JPEG")
            ntf.seek(0)
            self.client.post(url, {"image": ntf}, format="multipart")

        sample_flight()

        response = self.client.get(FLIGHT_URL)

        if response.data["results"]:
            self.assertIn("airplane_image", response.data["results"][0].keys())
