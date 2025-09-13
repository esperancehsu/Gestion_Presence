# tests/test_permissions.py
from django.test import TestCase
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient
from api.models import Employe, Presence, Rapport
from .utils import generate_jwt_token  # ← Importe l'utilitaire

User = get_user_model()

class PermissionTest(TestCase):
    def setUp(self):
        # Crée les utilisateurs
        self.admin = User.objects.create_user(username="admin", password="password", role="admin")
        self.rh = User.objects.create_user(username="rh", password="password", role="rh")
        self.manager = User.objects.create_user(username="manager", password="password", role="manager")
        self.staff = User.objects.create_user(username="staff", password="password", role="staff")

        # Crée les employés
        self.admin_employe = Employe.objects.create(user=self.admin, nom="Admin User")
        self.staff_employe = Employe.objects.create(user=self.staff, nom="Staff User")
        self.other_user = User.objects.create_user(username="other", password="password", role="staff")
        self.other_employe = Employe.objects.create(user=self.other_user, nom="Other User")

        # Crée une présence pour le staff
        self.staff_presence = Presence.objects.create(employe=self.staff_employe)
        # Crée une présence pour un autre employé
        self.other_presence = Presence.objects.create(employe=self.other_employe)

        self.client = APIClient()

    def authenticate(self, user):
        """Helper pour authentifier un utilisateur avec JWT"""
        token = generate_jwt_token(user.id)
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {token}')

    def test_admin_can_create_employee_for_other_user(self):
        self.authenticate(self.admin)  # ← Utilise authenticate
        response = self.client.post("/api/employes/", {
            "user_id": self.staff.id,
            "nom": "Test Employee",
            "poste": "Test Poste"
        })
        self.assertEqual(response.status_code, 201)

    def test_staff_cannot_create_employee_for_other_user(self):
        self.authenticate(self.staff)
        response = self.client.post("/api/employes/", {
            "user_id": self.admin.id,
            "nom": "Test Employee",
            "poste": "Test Poste"
        })
        self.assertEqual(response.status_code, 403)

    def test_staff_can_only_see_own_employee(self):
        self.authenticate(self.staff)
        response = self.client.get("/api/employes/")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['id'], self.staff_employe.id)

    def test_staff_can_create_own_presence(self):
        self.authenticate(self.staff)
        response = self.client.post("/api/presences/", {
            "note": "Test presence"
        })
        self.assertEqual(response.status_code, 201)

    def test_staff_cannot_modify_other_presence(self):
        self.authenticate(self.staff)
        response = self.client.put(f"/api/presences/{self.other_presence.id}/", {
            "note": "Modified by staff"
        })
        self.assertEqual(response.status_code, 403)

    def test_rh_can_delete_employee(self):
        self.authenticate(self.rh)
        response = self.client.delete(f"/api/employes/{self.other_employe.id}/")
        self.assertEqual(response.status_code, 204)

    def test_manager_cannot_delete_employee(self):
        self.authenticate(self.manager)
        response = self.client.delete(f"/api/employes/{self.other_employe.id}/")
        self.assertEqual(response.status_code, 403)