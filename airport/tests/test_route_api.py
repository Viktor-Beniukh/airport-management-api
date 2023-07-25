from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient

from airport.models import Route, Airport
from airport.serializers import RouteListSerializer
from airport.views import ApiPagination

ROUTE_URL = reverse("airport:route-list")


def sample_airport(**params):
    defaults = {
        "name": "Heathrow",
        "closest_big_city": "London",
    }
    defaults.update(params)

    return Airport.objects.create(**defaults)


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


class UnauthenticatedRouteApiTests(TestCase):
    def setUp(self) -> None:
        self.client = APIClient()

    def test_list_routs(self):
        sample_route()
        pagination = ApiPagination

        response = self.client.get(ROUTE_URL)

        routes = Route.objects.all()
        serializer = RouteListSerializer(pagination, routes, many=True)

        if serializer.is_valid():
            self.assertEqual(response.status_code, status.HTTP_200_OK)
            self.assertEqual(response.data, serializer.data)

    def test_filter_routes_by_source(self):
        pagination = ApiPagination

        airport1 = sample_airport(name="Rome")
        airport2 = sample_airport(name="Madrid")

        route1 = sample_route(source=airport1)
        route2 = sample_route(source=airport1)
        route3 = sample_route(source=airport2)

        response = self.client.get(ROUTE_URL, {"source": "Rome"})

        serializer1 = RouteListSerializer(pagination, route1)
        serializer2 = RouteListSerializer(pagination, route2)
        serializer3 = RouteListSerializer(pagination, route3)

        if serializer1.is_valid():
            self.assertIn(serializer1.data, response.data)
        if serializer2.is_valid():
            self.assertIn(serializer2.data, response.data)
        if serializer3.is_valid():
            self.assertNotIn(serializer3.data, response.data)

    def test_filter_routes_by_destination(self):
        pagination = ApiPagination

        airport1 = sample_airport(name="Rome")
        airport2 = sample_airport(name="Madrid")

        route1 = sample_route(destination=airport1)
        route2 = sample_route(destination=airport1)
        route3 = sample_route(destination=airport2)

        response = self.client.get(ROUTE_URL, {"destination": "Rome"})

        serializer1 = RouteListSerializer(pagination, route1)
        serializer2 = RouteListSerializer(pagination, route2)
        serializer3 = RouteListSerializer(pagination, route3)

        if serializer1.is_valid():
            self.assertIn(serializer1.data, response.data)
        if serializer2.is_valid():
            self.assertIn(serializer2.data, response.data)
        if serializer3.is_valid():
            self.assertNotIn(serializer3.data, response.data)


class AuthenticatedRouteApiTests(TestCase):
    def setUp(self) -> None:
        self.client = APIClient()
        self.user = get_user_model().objects.create_user(
            "test@test.com",
            "testpass"
        )
        self.client.force_authenticate(self.user)

    def test_create_route_forbidden(self):
        airport1 = Airport.objects.create(name="Airport 1")
        airport2 = Airport.objects.create(name="Airport 2")

        payload = {
            "source": airport1,
            "destination": airport2,
            "distance": 1000
        }

        response = self.client.post(ROUTE_URL, payload)

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)


class AdminRouteApiTests(TestCase):
    def setUp(self) -> None:
        self.client = APIClient()
        self.user = get_user_model().objects.create_user(
            "admin@test.com",
            "adminpass",
            is_staff=True
        )
        self.client.force_authenticate(self.user)

    def test_create_route(self):
        airport1 = Airport.objects.create(name="Airport 1")
        airport2 = Airport.objects.create(name="Airport 2")

        payload = {
            "source": airport1.id,
            "destination": airport2.id,
            "distance": 1000
        }

        response = self.client.post(ROUTE_URL, payload)

        route = Route.objects.get(id=response.data["id"])

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        for key in payload:
            if key in ("source", "destination"):
                self.assertEqual(int(payload[key]), getattr(route, key).id)
            else:
                self.assertEqual(payload[key], getattr(route, key))
