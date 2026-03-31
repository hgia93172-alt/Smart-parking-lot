from django.contrib.auth import get_user_model
from rest_framework.test import APITestCase


class AuthFlowTests(APITestCase):
    def setUp(self):
        self.user_password = "UserPass123!"
        self.admin_password = "AdminPass123!"

        self.user = get_user_model().objects.create_user(username="u1", password=self.user_password)
        self.admin = get_user_model().objects.create_user(username="admin", password=self.admin_password)
        self.admin.is_staff = True
        self.admin.save()

    def test_register_login_me_logout_flow(self):
        resp = self.client.post("/api/auth/register/", {"username": "u2", "password": self.user_password}, format="json")
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.data["code"], 20001)

        resp = self.client.post(
            "/api/auth/login/",
            {"username": "u2", "password": self.user_password},
            format="json",
        )
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.data["code"], 20001)
        token = resp.data["data"]["token"]
        self.client.credentials(HTTP_AUTHORIZATION=f"Token {token}")

        resp = self.client.get("/api/auth/me/")
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.data["code"], 20001)
        self.assertEqual(resp.data["data"]["username"], "u2")

        resp = self.client.patch("/api/auth/me/", {"role": "dev"}, format="json")
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.data["data"]["role"], "dev")

        resp = self.client.post("/api/auth/logout/", {}, format="json")
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.data["code"], 20001)

        resp = self.client.patch("/api/auth/me/", {"role": "x"}, format="json")
        self.assertEqual(resp.status_code, 401)
        self.assertEqual(resp.data["code"], 40101)

        resp = self.client.get("/api/auth/me/")
        self.assertEqual(resp.status_code, 401)
        self.assertEqual(resp.data["code"], 40101)

    def test_admin_user_management(self):
        resp = self.client.get("/api/auth/admin/users/")
        self.assertEqual(resp.status_code, 401)

        resp = self.client.post(
            "/api/auth/login/",
            {"username": "admin", "password": self.admin_password},
            format="json",
        )
        self.assertEqual(resp.status_code, 200)
        token = resp.data["data"]["token"]
        self.client.credentials(HTTP_AUTHORIZATION=f"Token {token}")

        resp = self.client.get("/api/auth/admin/users/")
        self.assertEqual(resp.status_code, 200)
        self.assertTrue(isinstance(resp.data["data"], list))

        resp = self.client.patch(f"/api/auth/admin/users/{self.user.id}/", {"role": "ops"}, format="json")
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.data["data"]["role"], "ops")

        resp = self.client.delete(f"/api/auth/admin/users/{self.user.id}/")
        self.assertEqual(resp.status_code, 200)