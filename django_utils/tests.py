import shutil
import tempfile

from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import override_settings
from rest_framework.test import APITestCase


class DjangoUtilsTests(APITestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls._media_root = tempfile.mkdtemp()
        cls._override = override_settings(MEDIA_ROOT=cls._media_root)
        cls._override.enable()

    @classmethod
    def tearDownClass(cls):
        try:
            if hasattr(cls, "_override"):
                cls._override.disable()
            shutil.rmtree(getattr(cls, "_media_root", ""), ignore_errors=True)
        finally:
            super().tearDownClass()

    def setUp(self):
        from django.contrib.auth import get_user_model

        self.user_password = "UserPass123!"
        self.admin_password = "AdminPass123!"
        self.user = get_user_model().objects.create_user(username="u_file", password=self.user_password)
        self.other = get_user_model().objects.create_user(username="u_other", password=self.user_password)
        self.admin = get_user_model().objects.create_user(username="a_file", password=self.admin_password)
        self.admin.is_staff = True
        self.admin.save()

    def _login_get_token(self, username: str, password: str) -> str:
        resp = self.client.post("/api/auth/login/", {"username": username, "password": password}, format="json")
        self.assertEqual(resp.status_code, 200)
        return resp.data["data"]["token"]

    def test_upload_download_delete_owner_flow(self):
        token = self._login_get_token(self.user.username, self.user_password)
        self.client.credentials(HTTP_AUTHORIZATION=f"Token {token}")

        upload_file = SimpleUploadedFile("hello.txt", b"hello world", content_type="text/plain")
        resp = self.client.post("/api/utils/files/upload/", {"file": upload_file}, format="multipart")
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.data["code"], 20001)
        file_id = resp.data["data"]["id"]

        resp = self.client.get("/api/utils/files/list/")
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.data["code"], 20001)
        self.assertTrue(any(item["id"] == file_id for item in resp.data["data"]))

        resp = self.client.get(f"/api/utils/files/{file_id}/download/")
        self.assertEqual(resp.status_code, 200)
        resp.close()

        resp = self.client.delete(f"/api/utils/files/{file_id}/")
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.data["code"], 20001)

        resp = self.client.get("/api/utils/files/list/")
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.data["code"], 20001)
        self.assertFalse(any(item["id"] == file_id for item in resp.data["data"]))

    def test_other_user_cannot_access_or_delete(self):
        token = self._login_get_token(self.user.username, self.user_password)
        self.client.credentials(HTTP_AUTHORIZATION=f"Token {token}")

        upload_file = SimpleUploadedFile("private.txt", b"private", content_type="text/plain")
        resp = self.client.post("/api/utils/files/upload/", {"file": upload_file}, format="multipart")
        self.assertEqual(resp.status_code, 200)
        file_id = resp.data["data"]["id"]

        token = self._login_get_token(self.other.username, self.user_password)
        self.client.credentials(HTTP_AUTHORIZATION=f"Token {token}")

        resp = self.client.get("/api/utils/files/list/")
        self.assertEqual(resp.status_code, 200)
        self.assertFalse(any(item["id"] == file_id for item in resp.data["data"]))

        resp = self.client.get(f"/api/utils/files/{file_id}/download/")
        self.assertEqual(resp.status_code, 403)
        self.assertEqual(resp.data["code"], 40301)

        resp = self.client.delete(f"/api/utils/files/{file_id}/")
        self.assertEqual(resp.status_code, 403)
        self.assertEqual(resp.data["code"], 40301)

    def test_admin_list_and_delete(self):
        token = self._login_get_token(self.user.username, self.user_password)
        self.client.credentials(HTTP_AUTHORIZATION=f"Token {token}")

        upload_file = SimpleUploadedFile("admin.txt", b"admin file", content_type="text/plain")
        resp = self.client.post("/api/utils/files/upload/", {"file": upload_file}, format="multipart")
        self.assertEqual(resp.status_code, 200)
        file_id = resp.data["data"]["id"]

        resp = self.client.get("/api/utils/admin/files/list/")
        self.assertEqual(resp.status_code, 403)
        self.assertEqual(resp.data["code"], 40301)

        token = self._login_get_token(self.admin.username, self.admin_password)
        self.client.credentials(HTTP_AUTHORIZATION=f"Token {token}")

        resp = self.client.get("/api/utils/admin/files/list/")
        self.assertEqual(resp.status_code, 200)
        self.assertTrue(isinstance(resp.data["data"], list))

        resp = self.client.delete(f"/api/utils/admin/files/{file_id}/")
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.data["code"], 20001)

        upload_file = SimpleUploadedFile("admin_can_download.txt", b"x", content_type="text/plain")
        resp = self.client.post("/api/utils/files/upload/", {"file": upload_file}, format="multipart")
        file_id = resp.data["data"]["id"]

        resp = self.client.get(f"/api/utils/files/{file_id}/download/")
        self.assertEqual(resp.status_code, 200)
        resp.close()