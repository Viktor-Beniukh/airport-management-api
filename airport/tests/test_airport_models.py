from decimal import Decimal

from django.contrib.auth import get_user_model
from django.test import TestCase

from airport.models import (
    AirplaneType,
    Airport,
    Airplane,
    Crew,
    Route,
    Flight,
    Order,
    Ticket,
    Payment
)


class ModelsTest(TestCase):

    def test_airplane_type_str(self) -> None:
        airplane_type = AirplaneType.objects.create(
            name="Compact",
        )
        self.assertEqual(str(airplane_type), airplane_type.name)

    def test_airport_str(self) -> None:
        airport = Airport.objects.create(name="Heathrow")

        self.assertEqual(str(airport), airport.name)

    def test_airplane_str(self) -> None:
        airplane_type = AirplaneType.objects.create(name="Compact")

        airplane = Airplane.objects.create(
            name="Boeing", rows=20, seats_in_row=8, airplane_type=airplane_type
        )

        self.assertEqual(str(airplane), airplane.name)

    def test_airplane_capacity_property(self):
        airplane_type = AirplaneType.objects.create(name="Compact")

        airplane = Airplane.objects.create(
            name="Boeing", rows=20, seats_in_row=8, airplane_type=airplane_type
        )
        expected_capacity = airplane.rows * airplane.seats_in_row

        self.assertEqual(airplane.capacity, expected_capacity)

    def test_crew_str(self) -> None:
        crew = Crew.objects.create(
            position="Captain", first_name="John", last_name="Smith"
        )
        self.assertEqual(
            str(crew),
            f"{crew.position}: "
            f"{crew.first_name} {crew.last_name}"
        )

    def test_crew_full_name_property(self):
        crew = Crew.objects.create(
            position="Captain", first_name="John", last_name="Smith"
        )
        expected_full_name = f"{crew.first_name} {crew.last_name}"

        self.assertEqual(crew.full_name, expected_full_name)

    def test_route_str(self) -> None:
        airport1 = Airport.objects.create(name="Heathrow")
        airport2 = Airport.objects.create(name="Denver")

        route = Route.objects.create(
            source=airport1, destination=airport2, distance=500
        )

        self.assertEqual(
            str(route),
            f"{route.id}: "
            f"{route.source} - {route.destination}"
        )

    def test_flight_str(self) -> None:
        airport1 = Airport.objects.create(name="Heathrow")
        airport2 = Airport.objects.create(name="Denver")
        airplane_type = AirplaneType.objects.create(name="Compact")

        airplane = Airplane.objects.create(
            name="Boeing", rows=20, seats_in_row=8, airplane_type=airplane_type
        )

        route = Route.objects.create(
            source=airport1, destination=airport2, distance=500
        )

        flight = Flight.objects.create(
            route=route, airplane=airplane
        )

        self.assertEqual(str(flight), str(flight.id))

    def test_order_str(self) -> None:
        user = get_user_model().objects.create_user(
            email="admin@user.com",
            password="admin12345",
        )
        order = Order.objects.create(user=user)

        self.assertEqual(str(order), str(order.created_at))

    def test_order_total_cost(self):
        user = get_user_model().objects.create_user(
            email="admin@user.com",
            password="admin12345",
        )
        airport3 = Airport.objects.create(name="Istanbul")
        airport4 = Airport.objects.create(name="Indira")
        airplane_type = AirplaneType.objects.create(name="Medium")

        airplane = Airplane.objects.create(
            name="Boeing", rows=20, seats_in_row=8, airplane_type=airplane_type
        )

        route = Route.objects.create(
            source=airport3, destination=airport4, distance=500
        )

        flight = Flight.objects.create(
            route=route, airplane=airplane
        )

        order = Order.objects.create(user=user)

        ticket1 = Ticket.objects.create(
            row=5, seat=6, flight=flight, order=order, price=100.00
        )
        ticket2 = Ticket.objects.create(
            row=5, seat=7, flight=flight, order=order, price=100.00
        )

        expected_total_cost = ticket1.get_cost() + ticket2.get_cost()

        self.assertEqual(order.total_cost(), expected_total_cost)

    def test_ticket_str(self) -> None:
        user = get_user_model().objects.create_user(
            email="admin@user.com",
            password="admin12345",
        )
        airport3 = Airport.objects.create(name="Istanbul")
        airport4 = Airport.objects.create(name="Indira")
        airplane_type = AirplaneType.objects.create(name="Medium")

        airplane = Airplane.objects.create(
            name="Boeing", rows=20, seats_in_row=8, airplane_type=airplane_type
        )

        route = Route.objects.create(
            source=airport3, destination=airport4, distance=500
        )

        flight = Flight.objects.create(
            route=route, airplane=airplane
        )

        order = Order.objects.create(user=user)

        ticket = Ticket.objects.create(
            row=5, seat=7, flight=flight, order=order
        )

        self.assertEqual(
            str(ticket),
            f"{str(ticket.flight)} "
            f"(row: {ticket.row}, seat: {ticket.seat})"
        )

    def test_ticket_get_cost(self):
        user = get_user_model().objects.create_user(
            email="admin@user.com",
            password="admin12345",
        )
        airport3 = Airport.objects.create(name="Istanbul")
        airport4 = Airport.objects.create(name="Indira")
        airplane_type = AirplaneType.objects.create(name="Medium")

        airplane = Airplane.objects.create(
            name="Boeing", rows=20, seats_in_row=8, airplane_type=airplane_type
        )

        route = Route.objects.create(
            source=airport3, destination=airport4, distance=500
        )

        flight = Flight.objects.create(
            route=route, airplane=airplane
        )

        order = Order.objects.create(user=user)

        ticket = Ticket.objects.create(
            row=5, seat=7, flight=flight, order=order, price=100.00
        )

        expected_cost = Decimal("100.00") * len(str(ticket.seat))

        self.assertEqual(ticket.get_cost(), expected_cost)

    def test_payment_str(self) -> None:
        user = get_user_model().objects.create_user(
            email="admin@user.com",
            password="admin12345",
        )
        order = Order.objects.create(user=user)

        payment = Payment.objects.create(order=order)

        self.assertEqual(
            str(payment),
            f"Payment {payment.id} "
            f"({payment.order_id} - {payment.order.user})"
        )
