# tests/test_auth.py
from django.test import TestCase
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient

User = get_user_model()

class AuthTest(TestCase):
    def setUp(self):
        self.client = APIClient()

    def test_register_user(self):
        response = self.client.post("/api/users/register/", {
            "username": "testuser",
            "email": "test@example.com",
            "password": "password123",
            "role": "staff"
        })
        self.assertEqual(response.status_code, 201)

    def test_login_user(self):
        # Crée un utilisateur
        user = User.objects.create_user(username="testuser", password="password123", role="staff")
        # Tente de se connecter
        response = self.client.post("/api/users/login/", {
            "username": "testuser",
            "password": "password123"
        })
        self.assertEqual(response.status_code, 200)
        self.assertIn("access", response.data)