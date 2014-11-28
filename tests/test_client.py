import requests
from unittest import TestCase

from devpi_plumber.server import TestServer
from devpi_plumber.client import DevpiClientError


class ClientTest(TestCase):

    def test_login_success(self):
        users = { "user": {"password": "secret"} }

        with TestServer(users) as devpi:
            self.assertIn("credentials valid", devpi.login("user", "secret"))

    def test_login_error(self):
        users = { "user": {"password": "secret"} }

        with TestServer(users) as devpi:
            with self.assertRaisesRegexp(DevpiClientError, "401 Unauthorized"):
                devpi.login('user', 'wrong password')

    def test_logoff(self):
        with TestServer() as devpi:
            self.assertIn("login information deleted", devpi.logoff())

    def test_use(self):
        with TestServer() as devpi:
            expected = "current devpi index: " + devpi.url + "/root/pypi"
            self.assertIn(expected, devpi.use("root/pypi"))

    def test_url(self):
        with TestServer() as devpi:
            devpi.use("root/pypi")
            self.assertEquals(devpi.server_url + "/root/pypi", devpi.url)

    def test_create_user(self):
        with TestServer() as devpi:
            devpi.create_user("user", password="password", email="user@example.com")
            self.assertEqual(200, requests.get(devpi.server_url + "/user").status_code)

    def test_modify_user(self):
        users = { "user": {"password": "secret"} }

        with TestServer(users) as devpi:
            devpi.modify_user("user", password="new secret")
            self.assertIn("credentials valid", devpi.login("user", "new secret"))

    def test_create_index(self):
        users = { "user": {"password": "secret"} }

        with TestServer(users) as devpi:
            devpi.create_index("user/index")
            self.assertEqual(200, requests.get(devpi.server_url + "/user/index").status_code)

    def test_modify_index(self):
        users = { "user": {"password": "secret"} }
        indices = { "user/index": { "bases": ""} }

        with TestServer(users, indices) as devpi:
            self.assertIn("changing bases", devpi.modify_index("user/index", bases="root/pypi"))

    def test_upload_file(self):
        users = { "user": {"password": "secret"} }
        indices = { "user/index": {} }

        with TestServer(users, indices) as devpi:
            devpi.login("user", "secret")
            devpi.use("user/index")
            devpi.upload("tests/fixture/package/dist/test-package-0.1.tar.gz")

            self.assertEqual(200, requests.get(devpi.server_url + "/user/index/+simple/test_package").status_code)

    def test_upload_folder(self):
        users = { "user": {"password": "secret"} }
        indices = { "user/index": {} }

        with TestServer(users, indices) as devpi:
            devpi.login("user", "secret")
            devpi.use("user/index")
            devpi.upload("tests/fixture/package/", directory=True)

            self.assertEqual(200, requests.get(devpi.server_url + "/user/index/+simple/test_package").status_code)

    def test_list_existing_package(self):
        users = { "user": {"password": "secret"} }
        indices = { "user/index": {} }

        with TestServer(users, indices) as devpi:
            devpi.login("user", "secret")
            devpi.use("user/index")
            devpi.upload("tests/fixture/package/", directory=True)

            expected = ['test_package-0.1-cp34-cp34m-linux_x86_64.whl', 'test-package-0.1.tar.gz']
            actual = devpi.list("test_package==0.1")

            self.assertEqual(len(actual), len(expected))
            for entry in actual:
                self.assertTrue(any(entry.endswith(package) for package in expected))

    def test_list_nonexisting_package(self):
        users = { "user": {"password": "secret"} }
        indices = { "user/index": {} }

        with TestServer(users, indices) as devpi:
            devpi.use("user/index")

            self.assertEqual([], devpi.list("test_package==0.1"))

    def test_replica(self):
        with TestServer(config={'port':2414}) as devpi:
            with TestServer(config={'master-url':devpi.server_url, 'port' : 2413}) as replica:

                self.assertNotEqual(devpi.server_url, replica.server_url)
