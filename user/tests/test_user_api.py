from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse
from rest_framework import status

from user.serializers import UserSerializer

USER_CREATE_URL = reverse("user:create")

User = get_user_model()


class UserSerializerTests(TestCase):
    def test_create_user_serializer(self):
        data = {
            "email": "test@test.com",
            "username": "testuser",
            "password": "testpassword",
            "first_name": "John",
            "last_name": "Doe",
            "is_staff": True
        }
        serializer = UserSerializer(data=data)
        self.assertTrue(serializer.is_valid())

        user = serializer.save()

        self.assertEqual(user.email, data["email"])
        self.assertEqual(user.username, data["username"])

    def test_update_user_serializer(self):
        user = User.objects.create_user(
            email="test@test.com",
            username="testuser",
            password="testpassword",
            first_name="John",
            last_name="Doe",
            is_staff=True
        )

        data = {
            "first_name": "Jane",
            "last_name": "Smith",
        }

        serializer = UserSerializer(user, data=data, partial=True)
        self.assertTrue(serializer.is_valid())

        updated_user = serializer.save()

        self.assertEqual(updated_user.first_name, data["first_name"])
        self.assertEqual(updated_user.last_name, data["last_name"])


class CreateUserViewTests(TestCase):
    def setUp(self):
        self.url = USER_CREATE_URL
        User.objects.all().delete()

    def test_create_user(self):
        data = {
            "email": "test@test.com",
            "username": "testuser",
            "password": "testpassword",
        }
        response = self.client.post(self.url, data)

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(User.objects.count(), 1)
