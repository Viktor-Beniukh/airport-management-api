import datetime

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from rest_framework import status
from rest_framework.test import APIClient

from airport.models import Order, Ticket, Airport, Route, AirplaneType, Airplane, Flight
from airport.serializers import OrderListSerializer
from airport.views import ApiPagination

ORDER_URL = reverse("airport:order-list")


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


def sample_order(**params):
    user = get_user_model().objects.create_user(
        email="user@test.com",
        password="testpass",
        username="UserTest"
    )

    defaults = {
        "user": user,
        "created_at": datetime.datetime
    }
    defaults.update(params)

    return Order.objects.create(**defaults)


class UnauthenticatedOrderApiTests(TestCase):
    def setUp(self):
        self.client = APIClient()

    def test_auth_required(self):
        response = self.client.get(ORDER_URL)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)


class AuthenticatedOrderApiTests(TestCase):
    def setUp(self) -> None:
        self.client = APIClient()
        self.user = get_user_model().objects.create_user(
            "test@test.com",
            "testpass"
        )
        self.client.force_authenticate(self.user)

    def test_list_orders(self):
        pagination = ApiPagination
        sample_order(user=self.user)

        response = self.client.get(ORDER_URL)

        orders = Order.objects.all()
        serializer = OrderListSerializer(pagination, orders, many=True)

        if serializer.is_valid():
            self.assertEqual(response.status_code, status.HTTP_200_OK)
            self.assertEqual(response.data, serializer.data)

    def test_create_order(self):
        order = sample_order(user=self.user)

        flight_1 = sample_flight()
        flight_2 = sample_flight()

        payload = {
            "id": order.id,
            "tickets": [
                {
                    "flight": flight_1.id,
                    "row": 5,
                    "seat": 1,
                    "price": 100.00
                },
                {
                    "flight": flight_2.id,
                    "row": 6,
                    "seat": 2,
                    "price": 100.00
                }
            ]
        }

        response = self.client.post(ORDER_URL, data=payload, format="json")

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        order = Order.objects.get(id=response.data["id"])

        for ticket_payload, order_ticket in zip(payload["tickets"], order.tickets.all()):
            for key in ticket_payload:
                if key == "flight":
                    self.assertEqual(ticket_payload[key], order_ticket.flight.id)
                else:
                    self.assertEqual(ticket_payload[key], getattr(order_ticket, key))
