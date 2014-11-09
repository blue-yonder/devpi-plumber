from unittest import TestCase

from devpi_plumber.server import TestServer
from devpi_plumber.client import DevpiClientException


class ClientTest(TestCase):

    def test_login_success(self):
        users = { 'user': {'password': "secret"} }

        with TestServer(users) as devpi:
            self.assertIn("credentials valid", devpi.login('user', 'secret'))

    def test_login_error(self):
        users = { 'user': {'password': "secret"} }

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
