from django.contrib import admin

from airport.models import (
    Airport,
    Route,
    AirplaneType,
    Airplane,
    Crew,
    Flight,
    Order,
    Ticket,
    Payment,
)


@admin.register(Airport)
class AirportAdmin(admin.ModelAdmin):
    list_display = ("name", "closest_big_city")
    list_filter = ("name",)
    search_fields = ("name", "closest_big_city")


@admin.register(Route)
class RouteAdmin(admin.ModelAdmin):
    list_display = ("source", "destination", "distance")
    list_filter = ("source", "destination",)
    search_fields = ("source", "destination",)


@admin.register(Airplane)
class AirplaneAdmin(admin.ModelAdmin):
    list_display = ("name", "airplane_type", "rows", "seats_in_row")
    list_filter = ("name", "airplane_type",)
    search_fields = ("name", "airplane_type",)


@admin.register(Crew)
class CrewAdmin(admin.ModelAdmin):
    list_display = ("position", "first_name", "last_name")
    list_filter = ("position",)
    search_fields = ("position",)


@admin.register(Flight)
class FlightAdmin(admin.ModelAdmin):
    list_display = ("airplane", "route", "departure_time", "arrival_time")
    list_filter = ("airplane", "route", "departure_time", "arrival_time")
    search_fields = ("airplane", "route",)


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ("user", "created_at")
    list_filter = ("created_at",)
    search_fields = ("created_at",)


@admin.register(Ticket)
class TicketAdmin(admin.ModelAdmin):
    list_display = ("order", "flight", "row", "seat", "price")
    list_filter = ("order", "flight", "price")


admin.site.register(AirplaneType)
admin.site.register(Payment)
