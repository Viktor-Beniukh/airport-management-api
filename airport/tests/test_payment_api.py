import datetime

from django.utils import timezone
from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from rest_framework import status
from rest_framework.test import APIClient

from airport.models import Order, Payment
from airport.serializers import PaymentSerializer
from airport.views import ApiPagination


PAYMENT_URL = reverse("airport:payment-list")


def sample_order(**params):
    user = get_user_model().objects.create_user(
        email="user@test.com",
        password="testpass",
        username="UserTest"
    )

    defaults = {
        "user": user,
        "created_at": timezone.now()
    }
    defaults.update(params)

    return Order.objects.create(**defaults)


def sample_payment(**params):
    order = sample_order()

    defaults = {
        "order": order,
        "date_payment": timezone.now()
    }
    defaults.update(params)

    return Payment.objects.create(**defaults)


def detail_url(payment_id):
    return reverse("airport:payment-detail", args=[payment_id])


class UnauthenticatedPaymentApiTests(TestCase):
    def setUp(self):
        self.client = APIClient()

    def test_auth_required(self):
        response = self.client.get(PAYMENT_URL)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)


class AuthenticatedPaymentApiTests(TestCase):
    def setUp(self) -> None:
        self.client = APIClient()
        self.user = get_user_model().objects.create_user(
            "test@test.com",
            "testpass"
        )
        self.client.force_authenticate(self.user)

    def test_list_payments(self):
        pagination = ApiPagination
        sample_payment()

        response = self.client.get(PAYMENT_URL)

        payments = Payment.objects.all()
        serializer = PaymentSerializer(pagination, payments, many=True)

        if serializer.is_valid():
            self.assertEqual(response.status_code, status.HTTP_200_OK)
            self.assertEqual(response.data, serializer.data)

    def test_retrieve_payment_detail(self):
        order = Order.objects.create(user=self.user)
        payment = sample_payment(order=order)

        url = detail_url(payment.id)
        response = self.client.get(url)

        serializer = PaymentSerializer(payment)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, serializer.data)

    def test_create_payment(self):
        order = Order.objects.create(user=self.user)

        payload = {
            "order": order.id,
        }

        response = self.client.post(PAYMENT_URL, payload)

        payment = Payment.objects.get(id=response.data["id"])

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        for key in payload:
            self.assertEqual(payload[key], getattr(payment, key).id)
