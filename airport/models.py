import os
import uuid

from django.core.exceptions import ValidationError
from django.conf import settings
from django.db import models
from django.utils.text import slugify


def airplane_image_file_path(instance, filename):
    _, extension = os.path.splitext(filename)
    filename = f"{slugify(instance.name)}-{uuid.uuid4()}{extension}"

    return os.path.join("uploads/airplanes/", filename)


class Airport(models.Model):
    name = models.CharField(max_length=255)
    closest_big_city = models.CharField(max_length=255)

    class Meta:
        ordering = ("name",)

    def __str__(self):
        return self.name


class Route(models.Model):
    source = models.ForeignKey(
        Airport, on_delete=models.CASCADE, related_name="route_source"
    )
    destination = models.ForeignKey(
        Airport, on_delete=models.CASCADE, related_name="route_destination"
    )
    distance = models.PositiveIntegerField()

    def __str__(self):
        return f"{self.id}: {self.source} - {self.destination}"


class AirplaneType(models.Model):
    name = models.CharField(max_length=50)

    def __str__(self):
        return self.name


class Airplane(models.Model):
    name = models.CharField(max_length=255)
    rows = models.PositiveIntegerField()
    seats_in_row = models.PositiveIntegerField()
    image = models.ImageField(
        null=True, upload_to=airplane_image_file_path
    )
    airplane_type = models.ForeignKey(
        AirplaneType, on_delete=models.CASCADE, related_name="airplanes"
    )

    @property
    def capacity(self) -> int:
        return self.rows * self.seats_in_row

    class Meta:
        ordering = ("name",)

    def __str__(self):
        return self.name


class Crew(models.Model):
    CAPTAIN = "Captain"
    FIRST_OFFICER = "First Officer"
    NAVIGATOR = "Navigator"
    FLIGHT_ENGINEER = "Flight Engineer"
    FLIGHT_ATTENDANT = "Flight Attendant"
    UNKNOWN = "unknown"

    POSITION_CHOICES = [
        (CAPTAIN, "Captain"),
        (FIRST_OFFICER, "First Officer"),
        (NAVIGATOR, "Navigator"),
        (FLIGHT_ENGINEER, "Flight Engineer"),
        (FLIGHT_ATTENDANT, "Flight Attendant"),
        (UNKNOWN, "unknown"),
    ]

    first_name = models.CharField(max_length=255)
    last_name = models.CharField(max_length=255)
    position = models.CharField(
        max_length=100, choices=POSITION_CHOICES, default=UNKNOWN
    )

    def __str__(self):
        return f"{self.position}: {self.first_name} {self.last_name}"

    @property
    def full_name(self):
        return f"{self.first_name} {self.last_name}"


class Flight(models.Model):
    route = models.ForeignKey(
        Route, on_delete=models.CASCADE, related_name="rout_flight"
    )
    airplane = models.ForeignKey(
        Airplane, on_delete=models.CASCADE, related_name="airplane_flight"
    )
    departure_time = models.DateTimeField(blank=True, null=True)
    arrival_time = models.DateTimeField(blank=True, null=True)
    crews = models.ManyToManyField(Crew, blank=True)

    def __str__(self):
        return str(self.id)


class Order(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE
    )

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return str(self.created_at)

    def total_cost(self):
        return sum(ticket.get_cost() for ticket in self.tickets.all())


class Ticket(models.Model):
    row = models.PositiveIntegerField()
    seat = models.PositiveIntegerField()
    price = models.DecimalField(
        max_digits=10, decimal_places=2, default=0
    )
    flight = models.ForeignKey(
        Flight, on_delete=models.CASCADE, related_name="flight_ticket"
    )
    order = models.ForeignKey(
        Order, on_delete=models.CASCADE, related_name="tickets"
    )

    @staticmethod
    def validate_ticket(row, seat, flight, error_to_raise):
        airplane = flight.airplane
        for ticket_attr_value, ticket_attr_name, airplane_attr_name in [
            (row, "row", "rows"),
            (seat, "seat", "seats_in_row"),
        ]:
            count_attrs = getattr(airplane, airplane_attr_name)
            if not (1 <= ticket_attr_value <= count_attrs):
                raise error_to_raise(
                    {
                        ticket_attr_name: f"{ticket_attr_name} "
                        f"number must be in available range: "
                        f"(1, {airplane_attr_name}): "
                        f"(1, {count_attrs})"
                    }
                )

    def clean(self):
        Ticket.validate_ticket(
            self.row,
            self.seat,
            self.flight,
            ValidationError,
        )

    def save(
            self,
            force_insert=False,
            force_update=False,
            using=None,
            update_fields=None,
    ):
        self.full_clean()
        return super(Ticket, self).save(
            force_insert, force_update, using, update_fields
        )

    class Meta:
        unique_together = ("flight", "row", "seat")
        ordering = ("row", "seat")

    def __str__(self):
        return (
            f"{str(self.flight)} (row: {self.row}, seat: {self.seat})"
        )

    def get_cost(self):
        return self.price * len(str(self.seat))


class Payment(models.Model):
    PENDING = "Pending"
    PAID = "Paid"
    CANCELLED = "Cancelled"

    STATUS_CHOICES = [
        (PENDING, "Pending"),
        (PAID, "Paid"),
        (CANCELLED, "Cancelled"),
    ]

    order = models.ForeignKey(
        Order, on_delete=models.CASCADE, related_name="payments"
    )
    status_payment = models.CharField(
        max_length=10, choices=STATUS_CHOICES, default=PENDING
    )
    date_payment = models.DateTimeField(auto_now_add=True, null=True)
    session_url = models.URLField(max_length=500, blank=True)
    session_id = models.CharField(max_length=255, blank=True)

    def __str__(self) -> str:
        return f"Payment {self.id} ({self.order_id} - {self.order.user})"
