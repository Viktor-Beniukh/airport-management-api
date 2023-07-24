from django.urls import path, include
from rest_framework import routers

from airport.views import (
    AirplaneTypeViewSet,
    AirplaneViewSet,
    AirportViewSet,
    RouteViewSet,
    CrewViewSet,
    FlightViewSet,
    OrderViewSet,
    PaymentViewSet,
    create_checkout_session,
    payment_success,
    payment_cancel,
)

router = routers.DefaultRouter()
router.register("airplane-types", AirplaneTypeViewSet)
router.register("airplanes", AirplaneViewSet)
router.register("airports", AirportViewSet)
router.register("routes", RouteViewSet)
router.register("crews", CrewViewSet)
router.register("flights", FlightViewSet)
router.register("orders", OrderViewSet)
router.register("payment", PaymentViewSet)

urlpatterns = [
    path("", include(router.urls)),
    path(
        "payment/<int:payment_id>/create-session/",
        create_checkout_session,
        name="create-session"
    ),
    path("success/", payment_success, name="success"),
    path("cancelled/", payment_cancel, name="cancelled"),
]

app_name = "airport"
