from django.db.models import F, Count
from rest_framework import viewsets, mixins, status
from rest_framework.decorators import action
from rest_framework.pagination import PageNumberPagination
from rest_framework.permissions import IsAdminUser
from rest_framework.response import Response

from airport.models import (
    AirplaneType,
    Airplane,
    Airport,
    Route,
    Crew,
    Flight,
    Order,
)
from airport.serializers import (
    AirplaneTypeSerializer,
    AirplaneSerializer,
    AirplaneListSerializer,
    AirplaneDetailSerializer,
    AirplaneImageSerializer,
    AirportSerializer,
    RouteSerializer,
    RouteListSerializer,
    CrewSerializer,
    CrewListSerializer,
    FlightSerializer,
    FlightListSerializer,
    FlightDetailSerializer,
    OrderSerializer,
    OrderListSerializer,
)


class ApiPagination(PageNumberPagination):
    page_size = 10
    max_page_size = 100


class AirplaneTypeViewSet(
    mixins.CreateModelMixin,
    viewsets.GenericViewSet
):
    queryset = AirplaneType.objects.all()
    serializer_class = AirplaneTypeSerializer

    def get_queryset(self):
        """Retrieve the airplane type with filter"""
        name = self.request.query_params.get("name")

        queryset = super().get_queryset()

        if name:
            queryset = queryset.filter(name__icontains=name)

        return queryset


class AirplaneViewSet(viewsets.ModelViewSet):
    queryset = Airplane.objects.select_related("airplane_type")
    serializer_class = AirplaneSerializer
    pagination_class = ApiPagination

    def get_queryset(self):
        """Retrieve the airplane with filter"""
        name = self.request.query_params.get("name")
        airplane_type = self.request.query_params.get("airplane_type")

        queryset = super().get_queryset()

        if name:
            queryset = queryset.filter(name__icontains=name)

        if airplane_type:
            queryset = queryset.filter(
                airplane_type__name__icontains=airplane_type
            )

        return queryset

    def get_serializer_class(self):
        if self.action == "list":
            return AirplaneListSerializer

        if self.action == "retrieve":
            return AirplaneDetailSerializer

        if self.action == "upload_image":
            return AirplaneImageSerializer

        return super().get_serializer_class()

    @action(
        methods=["POST"],
        detail=True,
        url_path="upload-image",
        permission_classes=[IsAdminUser],
    )
    def upload_image(self, request, pk=None):
        """Endpoint for uploading image to specific airplane"""
        airplane = self.get_object()
        serializer = self.get_serializer(airplane, data=request.data)

        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class AirportViewSet(
    mixins.ListModelMixin,
    mixins.CreateModelMixin,
    viewsets.GenericViewSet
):
    queryset = Airport.objects.all()
    serializer_class = AirportSerializer
    pagination_class = ApiPagination

    def get_queryset(self):
        """Retrieve the airport with filter"""
        name = self.request.query_params.get("name")

        queryset = super().get_queryset()

        if name:
            queryset = queryset.filter(name__icontains=name)

        return queryset


class RouteViewSet(
    mixins.ListModelMixin,
    mixins.CreateModelMixin,
    viewsets.GenericViewSet
):
    queryset = Route.objects.select_related("source", "destination")
    serializer_class = RouteSerializer
    pagination_class = ApiPagination

    def get_queryset(self):
        """Retrieve the route with filter"""
        source = self.request.query_params.get("source")
        destination = self.request.query_params.get("destination")

        queryset = super().get_queryset()

        if source:
            queryset = queryset.filter(
                source__name__icontains=source
            )

        if destination:
            queryset = queryset.filter(
                destination__name__icontains=destination
            )

        return queryset

    def get_serializer_class(self):
        if self.action == "list":
            return RouteListSerializer

        return super().get_serializer_class()


class CrewViewSet(viewsets.ModelViewSet):
    queryset = Crew.objects.all()
    serializer_class = CrewSerializer
    pagination_class = ApiPagination

    def get_queryset(self):
        """Retrieve the crew with filter"""
        position = self.request.query_params.get("position")

        queryset = super().get_queryset()

        if position:
            queryset = queryset.filter(position__icontains=position)

        return queryset

    def get_serializer_class(self):
        if self.action == "list":
            return CrewListSerializer

        return super().get_serializer_class()


class FlightViewSet(viewsets.ModelViewSet):
    queryset = (
        Flight.objects
        .prefetch_related(
            "route__source",
            "route__destination",
            "airplane__airplane_type",
            "crews"
        )
        .annotate(
            tickets_available=(
                F("airplane__rows") * F("airplane__seats_in_row")
                - Count("flight_ticket")
            )
        )
    )
    serializer_class = FlightSerializer
    pagination_class = ApiPagination

    def get_queryset(self):
        """Retrieve the flight with filter"""
        airplane = self.request.query_params.get("airplane")
        route_source = self.request.query_params.get("route_source")
        route_destination = self.request.query_params.get("route_destination")

        queryset = super().get_queryset()

        if airplane:
            queryset = queryset.filter(airplane__name__icontains=airplane)

        if route_source:
            queryset = queryset.filter(
                route__source__name__icontains=route_source
            )

        if route_destination:
            queryset = queryset.filter(
                route__destination__name__icontains=route_destination
            )

        return queryset

    def get_serializer_class(self):
        if self.action == "list":
            return FlightListSerializer

        if self.action == "retrieve":
            return FlightDetailSerializer

        return super().get_serializer_class()


class OrderViewSet(
    mixins.ListModelMixin,
    mixins.CreateModelMixin,
    viewsets.GenericViewSet
):
    queryset = Order.objects.prefetch_related(
        "tickets__flight__route__source",
        "tickets__flight__route__destination",
        "tickets__flight__airplane__airplane_type"
    )
    serializer_class = OrderSerializer
    pagination_class = ApiPagination

    def get_queryset(self):
        return Order.objects.filter(user=self.request.user)

    def get_serializer_class(self):
        if self.action == "list":
            return OrderListSerializer

        return super().get_serializer_class()

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)
