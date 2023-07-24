from django.contrib.auth import get_user_model
from django.test import TestCase

User = get_user_model()


class ModelTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            email="test@test.com",
            password="testpass",
            first_name="John",
            last_name="Doe"
        )

    def test_user_str(self) -> None:
        expected_str = self.user.email

        self.assertEqual(str(self.user), expected_str)

    def test_user_full_name_property(self) -> None:
        expected_full_name = f"{self.user.first_name} {self.user.last_name}"

        self.assertEqual(self.user.full_name, expected_full_name)
