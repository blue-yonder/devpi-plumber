import requests
from unittest import TestCase

from devpi_plumber.server import devpi_index, devpi_server, devpi_user


class ServerTest(TestCase):

    def test_server_start(self):
        with devpi_server() as server_url:
            self.assertEquals(200, requests.get(server_url).status_code)

    def test_user_creation(self):
        with devpi_server() as server_url:
            with devpi_user(server_url, "testuser") as user_url:
                self.assertEquals(200, requests.get(user_url).status_code)

    def test_index_creation(self):
        with devpi_server() as server_url:
            with devpi_user(server_url, "testuser"):
                with devpi_index(server_url, "testuser", "testindex") as index_url:
                    self.assertEquals(200, requests.get(index_url).status_code)
