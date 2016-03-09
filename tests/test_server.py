import requests
from unittest import TestCase

from devpi_plumber.server import TestServer


class ServerTest(TestCase):
    """
    Smoke test that the provided TestServer works expected.
    """
    def test_server_start(self):
        with TestServer() as devpi:
            self.assertEqual(200, requests.get(devpi.url).status_code)

    def test_user_creation(self):
        users = {
            'user1': {'password': 'secret1'},
            'user2': {'password': 'secret2'},
        }
        with TestServer(users) as devpi:
            self.assertEqual(200, requests.get(devpi.url + '/user1').status_code)
            self.assertEqual(200, requests.get(devpi.url + '/user2').status_code)
            self.assertEqual(404, requests.get(devpi.url + '/user3').status_code)

    def test_index_creation(self):
        users = {
            'user1': {'password': 'secret1'},
        }
        indices = {
            'user1/index1': {},
            'user1/index2': {},
        }
        with TestServer(users, indices) as devpi:
            self.assertEqual(200, requests.get(devpi.url + '/user1/index1').status_code)
            self.assertEqual(200, requests.get(devpi.url + '/user1/index2').status_code)
            self.assertEqual(404, requests.get(devpi.url + '/user1/index3').status_code)
