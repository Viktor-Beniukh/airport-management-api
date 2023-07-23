from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from rest_framework import status
from rest_framework.test import APIClient

from airport.models import Airport, Route, AirplaneType, Airplane, Flight
from airport.serializers import FlightListSerializer, FlightDetailSerializer
from airport.views import ApiPagination


FLIGHT_URL = reverse("airport:flight-list")


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


def detail_url(flight_id):
    return reverse("airport:flight-detail", args=[flight_id])


class UnauthenticatedFlightApiTests(TestCase):
    def setUp(self) -> None:
        self.client = APIClient()

    def test_list_flights(self):
        sample_flight()
        pagination = ApiPagination

        response = self.client.get(FLIGHT_URL)

        flights = Flight.objects.all()
        serializer = FlightListSerializer(pagination, flights, many=True)

        if serializer.is_valid():
            self.assertEqual(response.status_code, status.HTTP_200_OK)
            self.assertEqual(response.data, serializer.data)

    def test_retrieve_flight_detail(self):
        flight = sample_flight()

        url = detail_url(flight.id)
        response = self.client.get(url)

        serializer = FlightDetailSerializer(flight)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, serializer.data)

    def test_filter_flights_by_airplane_name(self):
        pagination = ApiPagination
        airplane1 = sample_airplane(name="Airbus 150")
        airplane2 = sample_airplane(name="Airbus 220")
        airplane3 = sample_airplane(name="Saab")

        flight1 = sample_flight(airplane=airplane1)
        flight2 = sample_flight(airplane=airplane2)
        flight3 = sample_flight(airplane=airplane3)

        response = self.client.get(FLIGHT_URL, {"airplane": "airbus"})

        serializer1 = FlightListSerializer(pagination, flight1)
        serializer2 = FlightListSerializer(pagination, flight2)
        serializer3 = FlightListSerializer(pagination, flight3)

        if serializer1.is_valid():
            self.assertIn(serializer1.data, response.data)
        if serializer2.is_valid():
            self.assertIn(serializer2.data, response.data)
        if serializer3.is_valid():
            self.assertNotIn(serializer3.data, response.data)

    def test_filter_flights_by_route_source(self):
        pagination = ApiPagination

        airport1 = sample_airport(name="Heathrow")
        airport2 = sample_airport(name="Denver")

        route1 = sample_route(source=airport1)
        route2 = sample_route(source=airport2)

        flight1 = sample_flight(route=route1)
        flight2 = sample_flight(route=route1)
        flight3 = sample_flight(route=route2)

        response = self.client.get(FLIGHT_URL, {"route_source": "heathrow"})

        serializer1 = FlightListSerializer(pagination, flight1)
        serializer2 = FlightListSerializer(pagination, flight2)
        serializer3 = FlightListSerializer(pagination, flight3)

        if serializer1.is_valid():
            self.assertIn(serializer1.data, response.data)
        if serializer2.is_valid():
            self.assertIn(serializer2.data, response.data)
        if serializer3.is_valid():
            self.assertNotIn(serializer3.data, response.data)

    def test_filter_flights_by_route_destination(self):
        pagination = ApiPagination

        airport1 = sample_airport(name="Heathrow")
        airport2 = sample_airport(name="Denver")

        route1 = sample_route(destination=airport1)
        route2 = sample_route(destination=airport2)

        flight1 = sample_flight(route=route1)
        flight2 = sample_flight(route=route1)
        flight3 = sample_flight(route=route2)

        response = self.client.get(FLIGHT_URL, {"route_destination": "heathrow"})

        serializer1 = FlightListSerializer(pagination, flight1)
        serializer2 = FlightListSerializer(pagination, flight2)
        serializer3 = FlightListSerializer(pagination, flight3)

        if serializer1.is_valid():
            self.assertIn(serializer1.data, response.data)
        if serializer2.is_valid():
            self.assertIn(serializer2.data, response.data)
        if serializer3.is_valid():
            self.assertNotIn(serializer3.data, response.data)


class AuthenticatedFlightApiTests(TestCase):
    def setUp(self) -> None:
        self.client = APIClient()
        self.user = get_user_model().objects.create_user(
            "test@test.com",
            "testpass"
        )
        self.client.force_authenticate(self.user)

    def test_create_flight_forbidden(self):
        route = sample_route()
        airplane = sample_airplane()

        payload = {
            "route": route,
            "airplane": airplane,
        }

        response = self.client.post(FLIGHT_URL, payload)

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)


class AdminFlightApiTests(TestCase):
    def setUp(self) -> None:
        self.client = APIClient()
        self.user = get_user_model().objects.create_user(
            "admin@test.com",
            "adminpass",
            is_staff=True
        )
        self.client.force_authenticate(self.user)

    def test_create_flight(self):
        route = sample_route()
        airplane = sample_airplane()

        payload = {
            "route": route.id,
            "airplane": airplane.id,
        }

        response = self.client.post(FLIGHT_URL, payload)

        flight = Flight.objects.get(id=response.data["id"])

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        for key in payload:
            self.assertEqual(int(payload[key]), getattr(flight, key).id)

    def test_update_flight(self):
        flight = sample_flight()

        url = detail_url(flight.id)
        new_route = sample_route()
        new_airplane = sample_airplane()
        payload = {
            "route": new_route.id,
            "airplane": new_airplane.id,
        }

        response = self.client.put(url, payload)

        flight.refresh_from_db()

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(flight.route.id, new_route.id)
        self.assertEqual(flight.airplane.id, new_airplane.id)

    def test_partial_update_flight(self):
        flight = sample_flight()

        url = detail_url(flight.id)
        new_route = sample_route()
        payload = {
            "route": new_route.id,
        }

        response = self.client.patch(url, payload)

        flight.refresh_from_db()

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(flight.route.id, new_route.id)

    def test_delete_flight(self):
        flight = sample_flight()

        url = detail_url(flight.id)

        response = self.client.delete(url)

        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
