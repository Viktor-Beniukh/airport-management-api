from rest_framework import serializers

from airport.models import (
    AirplaneType,
    Airport,
    Route,
    Airplane,
    Crew,
    Flight,
    Order,
    Ticket,
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
    airplane_type_name = serializers.CharField(source="airplane_type.name", read_only=True)

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
    airplane_name = serializers.CharField(source="airplane.name", read_only=True)
    route = serializers.StringRelatedField(read_only=True)
    departure_time = serializers.DateTimeField(format="%Y-%m-%d %H:%M")
    arrival_time = serializers.DateTimeField(format="%Y-%m-%d %H:%M")

    class Meta:
        model = Flight
        fields = (
            "id", "airplane_name", "route", "departure_time", "arrival_time"
        )


class FlightDetailSerializer(serializers.ModelSerializer):
    airplane = AirplaneDetailSerializer(read_only=True)
    route = RouteListSerializer(read_only=True)
    departure_time = serializers.DateTimeField(format="%Y-%m-%d %H:%M")
    arrival_time = serializers.DateTimeField(format="%Y-%m-%d %H:%M")

    class Meta:
        model = Flight
        fields = (
            "id", "airplane", "route", "departure_time", "arrival_time"
        )


class OrderSerializer(serializers.ModelSerializer):
    class Meta:
        model = Order
        fields = ("id", "created_at", "user",)


class TicketSerializer(serializers.ModelSerializer):
    class Meta:
        model = Ticket
        fields = (
            "id", "order", "flight", "row", "seat", "price"
        )
