import os.path
import unittest
from time import time
from unittest.mock import Mock, patch

from xero import Xero
from xero.auth import OAuth2Credentials


class FilesManagerTest(unittest.TestCase):
    def setUp(self):
        super().setUp()
        # Create an expired token to be used by tests
        self.expired_token = {
            "access_token": "1234567890",
            "expires_in": 1800,
            "token_type": "Bearer",
            "refresh_token": "0987654321",
            "expires_at": time(),
        }

        self.filepath = "test_file.txt"
        with open(self.filepath, "w") as f:
            f.write("test")

    def tearDown(self):
        os.remove(self.filepath)

    @patch("requests.get")
    def test_tenant_is_used_in_xero_request(self, r_get):
        credentials = OAuth2Credentials(
            "client_id", "client_secret", token=self.expired_token, tenant_id="12345"
        )
        xero = Xero(credentials)
        r_get.return_value = Mock(
            status_code=200,
            headers={"content-type": "text/html; charset=utf-8"},
        )
        xero.filesAPI.files.all()

        self.assertEqual(r_get.call_args[1]["headers"]["Xero-tenant-id"], "12345")

    @patch("requests.post")
    def test_upload_file_as_path(self, r_get):
        credentials = OAuth2Credentials(
            "client_id", "client_secret", token=self.expired_token, tenant_id="12345"
        )
        xero = Xero(credentials)
        r_get.return_value = Mock(
            status_code=200,
            headers={"content-type": "text/html; charset=utf-8"},
        )
        xero.filesAPI.files.upload_file(path=self.filepath)

        self.assertIn(self.filepath, r_get.call_args[1]["files"])

    @patch("requests.post")
    def test_upload_file_as_file(self, r_get):
        credentials = OAuth2Credentials(
            "client_id", "client_secret", token=self.expired_token, tenant_id="12345"
        )
        xero = Xero(credentials)
        r_get.return_value = Mock(
            status_code=200,
            headers={"content-type": "text/html; charset=utf-8"},
        )

        with open(self.filepath) as f:
            xero.filesAPI.files.upload_file(
                file=f, filename=os.path.basename(self.filepath)
            )

        self.assertIn(self.filepath, r_get.call_args[1]["files"])
