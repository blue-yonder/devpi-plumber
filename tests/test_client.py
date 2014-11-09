import requests
from unittest import TestCase

from devpi_plumber.server import TestServer
from devpi_plumber.client import DevpiClientException


class ClientTest(TestCase):

    def test_login_success(self):
        users = { "user": {"password": "secret"} }

        with TestServer(users) as devpi:
            self.assertIn("credentials valid", devpi.login("user", "secret"))

    def test_login_error(self):
        users = { "user": {"password": "secret"} }

        with TestServer(users) as devpi:
            with self.assertRaisesRegexp(DevpiClientException, "401 Unauthorized"):
                devpi.login('user', 'wrong password')

    def test_logoff(self):
        with TestServer() as devpi:
            self.assertIn("login information deleted", devpi.logoff())

    def test_use(self):
        with TestServer() as devpi:
            expected = "current devpi index: " + devpi.url + "/root/pypi"
            self.assertIn(expected, devpi.use("root/pypi"))

    def test_create_user(self):
        with TestServer() as devpi:
            devpi.create_user("user", password="password", email="user@example.com")
            self.assertEquals(200, requests.get(devpi.url + "/user").status_code)

    def test_modify_user(self):
        users = { "user": {"password": "secret"} }

        with TestServer(users) as devpi:
            devpi.modify_user("user", password="new secret")
            self.assertIn("credentials valid", devpi.login("user", "new secret"))

    def test_create_index(self):
        users = { "user": {"password": "secret"} }

        with TestServer(users) as devpi:
            devpi.create_index("user/index")
            self.assertEquals(200, requests.get(devpi.url + "/user/index").status_code)

    def test_modify_index(self):
        users = { "user": {"password": "secret"} }
        indices = { "user/index": { "bases": ""} }

        with TestServer(users, indices) as devpi:
            self.assertIn("changing bases", devpi.modify_index("user/index", bases="root/pypi"))

    def test_upload_file(self):
        users = { "user": {"password": "secret"} }
        indices = { "user/index": {} }

        with TestServer(users, indices) as devpi:
            devpi.use("user/index")
            self.assertEqual("", devpi.upload('tests/fixture/package/dist/test_package-0.1_dev-cp27-none-linux_x86_64.whl'))

    def test_upload_folder(self):
        users = { "user": {"password": "secret"} }
        indices = { "user/index": {} }

        with TestServer(users, indices) as devpi:
            devpi.use("user/index")
            self.assertEqual("", devpi.upload('tests/fixture/package/', directory=True))
