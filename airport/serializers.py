from django.db import transaction
from rest_framework import serializers
from rest_framework.exceptions import ValidationError

from airport.models import (
    AirplaneType,
    Airport,
    Route,
    Airplane,
    Crew,
    Flight,
    Order,
    Ticket,
    Payment,
)


class AirplaneTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = AirplaneType
        fields = ("id", "name")


class AirportSerializer(serializers.ModelSerializer):
    class Meta:
        model = Airport
        fields = ("id", "name", "closest_big_city")


class RouteSerializer(serializers.ModelSerializer):
    class Meta:
        model = Route
        fields = ("id", "source", "destination", "distance")


class RouteListSerializer(serializers.ModelSerializer):
    source = AirportSerializer(read_only=True)
    destination = AirportSerializer(read_only=True)

    class Meta:
        model = Route
        fields = ("id", "source", "destination", "distance")


class AirplaneSerializer(serializers.ModelSerializer):
    class Meta:
        model = Airplane
        fields = (
            "id", "name", "airplane_type", "rows", "seats_in_row",
        )


class AirplaneListSerializer(serializers.ModelSerializer):
    airplane_type_name = serializers.CharField(
        source="airplane_type.name", read_only=True
    )

    class Meta:
        model = Airplane
        fields = (
            "id",
            "name",
            "airplane_type_name",
            "image",
            "rows",
            "seats_in_row",
            "capacity"
        )


class AirplaneDetailSerializer(serializers.ModelSerializer):
    airplane_type = AirplaneTypeSerializer(many=False, read_only=True)

    class Meta:
        model = Airplane
        fields = (
            "id",
            "name",
            "airplane_type",
            "image",
            "rows",
            "seats_in_row",
            "capacity"
        )


class AirplaneImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = Airplane
        fields = ("id", "image")


class CrewSerializer(serializers.ModelSerializer):
    class Meta:
        model = Crew
        fields = (
            "id", "position", "first_name", "last_name",
        )


class CrewListSerializer(serializers.ModelSerializer):
    class Meta:
        model = Crew
        fields = (
            "id", "position", "full_name",
        )


class FlightSerializer(serializers.ModelSerializer):
    class Meta:
        model = Flight
        fields = (
            "id", "airplane", "route", "departure_time", "arrival_time"
        )


class FlightListSerializer(serializers.ModelSerializer):
    airplane_name = serializers.CharField(
        source="airplane.name", read_only=True
    )
    airplane_type = serializers.CharField(
        source="airplane.airplane_type.name", read_only=True
    )
    airplane_image = serializers.ImageField(
        source="airplane.image", read_only=True
    )
    route = serializers.StringRelatedField(read_only=True)
    departure_time = serializers.DateTimeField(format="%Y-%m-%d %H:%M")
    arrival_time = serializers.DateTimeField(format="%Y-%m-%d %H:%M")
    airplane_capacity = serializers.IntegerField(
        source="airplane.capacity", read_only=True
    )
    tickets_available = serializers.IntegerField(read_only=True)

    class Meta:
        model = Flight
        fields = (
            "id",
            "airplane_name",
            "airplane_type",
            "airplane_image",
            "route",
            "departure_time",
            "arrival_time",
            "airplane_capacity",
            "tickets_available"
        )


class TicketSerializer(serializers.ModelSerializer):

    def validate(self, attrs):
        data = super(TicketSerializer, self).validate(attrs=attrs)

        Ticket.validate_ticket(
            attrs["row"],
            attrs["seat"],
            attrs["flight"],
            ValidationError,
        )

        return data

    class Meta:
        model = Ticket
        fields = (
            "id", "flight", "row", "seat", "price"
        )


class TicketSeatsSerializer(TicketSerializer):
    class Meta:
        model = Ticket
        fields = ("row", "seat")


class TicketListSerializer(TicketSerializer):
    flight = FlightListSerializer(many=False, read_only=True)


class FlightDetailSerializer(serializers.ModelSerializer):
    airplane = AirplaneListSerializer(many=False, read_only=True)
    crews = CrewListSerializer(many=True, read_only=True)
    route = RouteListSerializer(many=False, read_only=True)
    departure_time = serializers.DateTimeField(format="%Y-%m-%d %H:%M")
    arrival_time = serializers.DateTimeField(format="%Y-%m-%d %H:%M")
    taken_places = TicketSeatsSerializer(
        source="flight_ticket", many=True, read_only=True
    )

    class Meta:
        model = Flight
        fields = (
            "id",
            "airplane",
            "crews",
            "route",
            "departure_time",
            "arrival_time",
            "taken_places"
        )


class PaymentSerializer(serializers.ModelSerializer):
    order = serializers.PrimaryKeyRelatedField(
        queryset=Order.objects.select_related("user")
    )
    user_full_name = serializers.CharField(
        source="order.user.full_name", read_only=True
    )
    status_payment = serializers.CharField(read_only=True)
    date_payment = serializers.DateTimeField(format="%Y-%m-%d %H:%M", read_only=True)
    session_url = serializers.URLField(read_only=True)
    session_id = serializers.CharField(read_only=True)

    class Meta:
        model = Payment
        fields = (
            "id",
            "order",
            "user_full_name",
            "status_payment",
            "date_payment",
            "session_url",
            "session_id",
        )


class PaymentListSerializer(PaymentSerializer):
    date_payment = serializers.DateTimeField(format="%Y-%m-%d %H:%M")

    class Meta:
        model = Payment
        fields = ("status_payment", "date_payment")


class PaymentUpdateSerializer(PaymentSerializer):
    order = serializers.PrimaryKeyRelatedField(
        many=False, read_only=True
    )
    session_url = serializers.URLField(read_only=True)
    session_id = serializers.CharField(read_only=True)


class OrderSerializer(serializers.ModelSerializer):
    tickets = TicketSerializer(
        many=True, read_only=False, allow_empty=False
    )
    total_cost = serializers.DecimalField(
        max_digits=10, decimal_places=2, read_only=True
    )
    payments = PaymentListSerializer(many=True, read_only=True)

    class Meta:
        model = Order
        fields = ("id", "tickets", "created_at", "total_cost", "payments")

    def create(self, validated_data):
        with transaction.atomic():
            tickets_data = validated_data.pop("tickets")
            order = Order.objects.create(**validated_data)
            for ticket_data in tickets_data:
                Ticket.objects.create(order=order, **ticket_data)
            return order


class OrderListSerializer(OrderSerializer):
    tickets = TicketListSerializer(many=True, read_only=True)
    created_at = serializers.DateTimeField(format="%Y-%m-%d %H:%M")
