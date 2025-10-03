from tokenize import TokenError
from django.urls import reverse
from django.contrib.auth.models import User
from rest_framework import status
from rest_framework.test import APITestCase

class UserAuthAPITests(APITestCase):
    def setUp(self):
        self.register_url = reverse("register")
        self.login_url = reverse("login")
        self.logout_url = reverse("logout")
        self.contact_url = reverse("contact")
        self.user_data = {
            "username": "testuser",
            "email": "testuser@example.com",
            "first_name": "Test",
            "last_name": "User",
            "password": "StrongPass123!",
            "confirm_password": "StrongPass123!"
        }
        self.user = User.objects.create_user(username="existing", email="existing@example.com", password="password123")

    def test_register_user_success(self):
        response = self.client.post(self.register_url, self.user_data, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(User.objects.filter(username="testuser").exists(), True)

    def test_register_user_password_mismatch(self):
        data = self.user_data.copy()
        data["confirm_password"] = "WrongPass123!"
        response = self.client.post(self.register_url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("password", response.data)

    def test_register_user_existing_email(self):
        data = self.user_data.copy()
        data["email"] = "existing@example.com"
        response = self.client.post(self.register_url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("email", response.data)

    def test_login_success(self):
        user = User.objects.create_user(username="loginuser", password="LoginPass123")
        data = {"username": "loginuser", "password": "LoginPass123"}
        response = self.client.post(self.login_url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("access", response.data)
        self.assertIn("refresh", response.data)
        self.access_token = response.data["access"]
        self.refresh_token = response.data["refresh"]

    def test_login_failure(self):
        data = {"username": "nonexist", "password": "wrongpass"}
        response = self.client.post(self.login_url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_logout_success(self):
        user = User.objects.create_user(username="logoutuser", password="LogoutPass123")
        data = {"username": "logoutuser", "password": "LogoutPass123"}
        login_response = self.client.post(self.login_url, data, format="json")
        refresh_token = login_response.data["refresh"]
        response = self.client.post(self.logout_url, {"refresh": refresh_token}, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_contact_success(self):
        data = {
            "name": "John Doe",
            "email": "john@example.com",
            "message": "Hello there"
        }
        response = self.client.post(self.contact_url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("success", response.data)

    def test_contact_missing_fields(self):
        data = {"name": "John Doe"}
        response = self.client.post(self.contact_url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
