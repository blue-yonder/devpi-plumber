import requests
from twitter.common.contextutil import pushd
from unittest import TestCase

from devpi_plumber.client import (DevpiClient, DevpiClientError, DevpiCommandWrapper,
                                  volatile_index)
from devpi_plumber.server import TestServer


class ClientTest(TestCase):
    """
    Assert that the plumber devpi client behaves as expected.
    """
    def test_user_session(self):
        users = {"user": {"password": "secret"}}

        with TestServer(users) as devpi:
            self.assertEquals('root', devpi.user)
            with devpi.user_session('user', 'secret'):
                self.assertEquals("user", devpi.user)
            self.assertIsNone(devpi.user)

    def test_devpi_client(self):
        with TestServer() as test_server:
            with DevpiClient(test_server.server_url) as devpi:
                devpi.create_user("user", password="password", email="user@example.com")
                self.assertEqual(200, requests.get(devpi.server_url + "/user").status_code)
                self.assertIn("credentials valid", devpi.login("user", "password"))
                self.assertEquals("user", devpi.user)

    def test_login_success(self):
        users = {"user": {"password": "secret"}}

        with TestServer(users) as devpi:
            self.assertIn("credentials valid", devpi.login("user", "secret"))
            self.assertEquals("user", devpi.user)

    def test_login_error(self):
        users = {"user": {"password": "secret"}}

        with TestServer(users) as devpi:
            with self.assertRaisesRegexp(DevpiClientError, "401 Unauthorized"):
                devpi.login('user', 'wrong password')
            self.assertEquals('root', devpi.user)

    def test_logoff(self):
        with TestServer() as devpi:
            self.assertIn("login information deleted", devpi.logoff())
            self.assertIsNone(devpi.user)

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

    def test_delete_user(self):
        users = {"user": {"password": "secret"}}

        with TestServer(users) as devpi:
            devpi.create_index("user/index")
            devpi.delete_user("user")
            self.assertEqual(['root'], devpi.list_users())
            self.assertEqual(['root/pypi'], devpi.list_indices())

    def test_modify_user(self):
        users = {"user": {"password": "secret"}}

        with TestServer(users) as devpi:
            devpi.modify_user("user", password="new secret")
            self.assertIn("credentials valid", devpi.login("user", "new secret"))

    def test_list_users(self):
        users = {"user": {"password": "secret"}}

        with TestServer(users) as devpi:
            self.assertEqual(sorted(['root', 'user']), sorted(devpi.list_users()))

    def test_create_index(self):
        users = {"user": {"password": "secret"}}

        with TestServer(users) as devpi:
            devpi.create_index("user/index")
            self.assertEqual(200, requests.get(devpi.server_url + "/user/index").status_code)

    def test_delete_index(self):
        users = {"user": {"password": "secret"}}

        with TestServer(users) as devpi:
            devpi.create_index("user/index")
            self.assertEqual(200, requests.get(devpi.server_url + "/user/index").status_code)
            devpi.delete_index("user/index")
            self.assertEqual(['root/pypi'], devpi.list_indices())

    def test_modify_index(self):
        users = {"user": {"password": "secret"}}
        indices = {"user/index": {"bases": ""}}

        with TestServer(users, indices) as devpi:
            self.assertIn("bases=root/pypi", devpi.modify_index("user/index", bases="root/pypi"))

    def test_list_indices(self):
        users = {"user": {"password": "secret"}}
        indices = {"user/index": {}}

        with TestServer(users, indices) as devpi:
            listed = devpi.list_indices()
            self.assertEquals(2, len(listed))
            self.assertIn('root/pypi', listed)
            self.assertIn('user/index', listed)

    def test_list_indices_by_user(self):
        users = {"user": {"password": "secret"}}
        indices = {"user/index": {}, "user/index2": {}}

        with TestServer(users, indices) as devpi:
            listed = devpi.list_indices(user='root')
            self.assertListEqual(['root/pypi'], listed)

            listed = devpi.list_indices(user='user')
            self.assertSetEqual({'user/index', 'user/index2'}, set(listed))

    def test_upload_file(self):
        users = {"user": {"password": "secret"}}
        indices = {"user/index": {}}

        with TestServer(users, indices) as devpi:
            devpi.login("user", "secret")
            devpi.use("user/index")
            devpi.upload("tests/fixture/dist/test-package-0.1.tar.gz")

            self.assertEqual(200, requests.get(devpi.server_url + "/user/index/+simple/test_package").status_code)

    def test_upload_folder(self):
        users = {"user": {"password": "secret"}}
        indices = {"user/index": {}}

        with TestServer(users, indices) as devpi:
            devpi.login("user", "secret")
            devpi.use("user/index")
            devpi.upload("tests/fixture/dist/", directory=True)

            self.assertEqual(200, requests.get(devpi.server_url + "/user/index/+simple/test_package").status_code)

    def test_upload_dry_run(self):
        users = {"user": {"password": "secret"}}
        indices = {"user/index": {}}

        with TestServer(users, indices) as devpi:
            devpi.login("user", "secret")
            devpi.use("user/index")
            devpi.upload("tests/fixture/dist/test-package-0.1.tar.gz", dry_run=True)

            self.assertIn('Not Found', requests.get(devpi.server_url + "/user/index/+simple/test_package").text)

    def test_upload_with_docs(self):
        users = {"user": {"password": "secret"}}
        indices = {"user/index": {}}

        with TestServer(users, indices) as devpi:
            devpi.login("user", "secret")
            devpi.use("user/index")
            with pushd('tests/fixture/package'):
                devpi.upload(with_docs=True)

    def test_list_existing_package(self):
        users = {"user": {"password": "secret"}}
        indices = {"user/index": {}}

        with TestServer(users, indices) as devpi:
            devpi.login("user", "secret")
            devpi.use("user/index")
            devpi.upload("tests/fixture/dist/", directory=True)

            expected = ['test_package-0.1-py2.py3-none-any.whl', 'test-package-0.1.tar.gz']
            actual = devpi.list("test_package==0.1")

            self.assertEqual(len(actual), len(expected))
            for entry in actual:
                self.assertTrue(any(entry.endswith(package) for package in expected))

    def test_list_nonexisting_package(self):
        users = {"user": {"password": "secret"}}
        indices = {"user/index": {}}

        with TestServer(users, indices) as devpi:
            devpi.use("user/index")

            self.assertEqual([], devpi.list("test_package==0.1"))

    def test_list_error(self):
        users = {"user": {"password": "secret"}}
        indices = {"user/index": {}}

        with TestServer(users, indices) as devpi:
            with self.assertRaisesRegexp(DevpiClientError, "not connected to an index"):
                devpi.list("test_package==0.1")

    def test_replica(self):
        with TestServer(config={'port': 2414, 'role': 'master'}) as devpi:
            with TestServer(config={'master-url': devpi.server_url, 'port': 2413}) as replica:

                self.assertNotEqual(devpi.server_url, replica.server_url)

    def test_remove(self):
        users = {"user": {"password": "secret"}}
        indices = {"user/index": {}}

        with TestServer(users, indices) as devpi:
            devpi.login("user", "secret")
            devpi.use("user/index")
            devpi.upload("tests/fixture/dist/", directory=True)

            devpi.remove("test_package==0.1")

            self.assertListEqual([], devpi.list("test_package==0.1"))

    def test_remove_invalid(self):
        users = {"user": {"password": "secret"}}
        indices = {"user/index": {}}

        with TestServer(users, indices) as devpi:
            devpi.login("user", "secret")
            devpi.use("user/index")
            devpi.upload("tests/fixture/dist/", directory=True)

            devpi.remove("test_package==0.2")

            self.assertEquals(2, len(devpi.list("test_package==0.1")))

    def test_get_json(self):
        users = {"user": {"password": "secret"}}
        indices = {"user/index": {}}

        with TestServer(users, indices) as devpi:
            root = devpi.get_json('/')
            self.assertEquals(root['type'], 'list:userconfig')
            self.assertIn('root', root['result'])
            self.assertIn('user', root['result'])

            with self.assertRaises(DevpiClientError):
                devpi.get_json('/foo')

            user = devpi.get_json('/user')
            self.assertEquals(user['type'], 'userconfig')
            self.assertIn('index', user['result']['indexes'])

            with self.assertRaises(DevpiClientError):
                devpi.get_json('/user/foo')

            index = devpi.get_json('/user/index')
            self.assertEquals(index['type'], 'indexconfig')
            self.assertListEqual(index['result']['acl_upload'], ['user'])
            self.assertListEqual(index['result']['projects'], [])

            with self.assertRaises(DevpiClientError):
                devpi.get_json('/user/index/test-package')
            with self.assertRaises(DevpiClientError):
                devpi.get_json('/user/index/test-package/0.1')

            devpi.login("user", "secret")
            devpi.use("user/index")
            devpi.upload("tests/fixture/dist/", directory=True)

            index = devpi.get_json('/user/index')
            self.assertListEqual(index['result']['projects'], ['test-package'])

            package = devpi.get_json('/user/index/test-package')
            self.assertEquals(package['type'], 'projectconfig')
            self.assertIn('0.1', package['result'])

            version = devpi.get_json('/user/index/test-package/0.1')
            self.assertEquals(version['type'], 'versiondata')
            links = '\n'.join([link['href'] for link in version['result']['+links']])
            self.assertIn('test_package-0.1-py2.py3-none-any.whl', links)
            self.assertIn('test-package-0.1.doc.zip', links)

            with self.assertRaises(DevpiClientError):
                devpi.get_json('/user/index/test-package/0.2')


class VolatileIndexTests(TestCase):

    def test_set_unset_volatile_flag(self):
        index = "user/index"
        users = {"user": {"password": "secret"}}
        indices = {index: {'volatile': False}}

        with TestServer(users, indices) as client:
            client.login("user", "secret")

            with volatile_index(client, index):
                self.assertIn('volatile=True', client.modify_index(index))
            self.assertIn('volatile=False', client.modify_index(index))

            with self.assertRaises(Exception):
                with volatile_index(client, 'user/index'):
                    raise Exception("Woops")
            self.assertIn('volatile=False', client.modify_index(index))

    def test_throw_when_not_forced(self):
        index = "user/index"
        users = {"user": {"password": "secret"}}
        indices = {index: {'volatile': False}}

        with TestServer(users, indices) as client:
            client.login("user", "secret")

            with self.assertRaises(Exception):
                with volatile_index(client, 'user/index', force_volatile=False):
                    pass
            self.assertIn('volatile=False', client.modify_index(index))


class DevpiCommandWrapperTest(TestCase):
    def setUp(self):
        # monkey patch DevpiCommandWrapper _execute just returns the command
        # that would be executed.
        def _echo_execute(*args, **kwargs):
            return DevpiCommandWrapper._create_command(*args, **kwargs)

        self._original_execute = DevpiCommandWrapper._execute
        DevpiCommandWrapper._execute = _echo_execute

    def tearDown(self):
        # undo monkey patch
        DevpiCommandWrapper._execute = self._original_execute

    def test_use(self):
        dcw = DevpiCommandWrapper('http://localhost/', '/example')
        self.assertEqual(
            dcw.use('hans/prod'),
            ['devpi', 'use', 'http://localhost/hans/prod',
             '--clientdir=/example'])

    def test_use_client_cert(self):
        dcw = DevpiCommandWrapper('http://localhost/', '/example',
                                  client_cert='/path/to/cert')
        self.assertEqual(
            dcw.use('hans/prod'),
            ['devpi', 'use', 'http://localhost/hans/prod',
             '--client-cert=/path/to/cert', '--clientdir=/example'])

    def test_login(self):
        dcw = DevpiCommandWrapper('http://localhost/', '/example')
        self.assertEqual(
            dcw.login('hans', 'secret'),
            ['devpi', 'login', 'hans', '--password',
             'secret', '--clientdir=/example'])

    def test_logoff(self):
        dcw = DevpiCommandWrapper('http://localhost/', '/example')
        self.assertEqual(dcw.logoff(),
                         ['devpi', 'logoff', '--clientdir=/example'])

    def test_create_user(self):
        dcw = DevpiCommandWrapper('http://localhost/', '/example')
        self.assertEqual(
            dcw.create_user('hans', bar='baz'),
            ['devpi', 'user', '--create', 'hans',
             'bar=baz', '--clientdir=/example'])

    def test_modify_user(self):
        dcw = DevpiCommandWrapper('http://localhost/', '/example')
        self.assertEqual(
            dcw.modify_user('hans', foo='bar'),
            ['devpi', 'user', '--modify', 'hans',
             'foo=bar', '--clientdir=/example'])

    def test_create_index(self):
        dcw = DevpiCommandWrapper('http://localhost/', '/example')
        self.assertEqual(
            dcw.create_index('myindex', bases='/emilie/prod', volatile=False),
            ['devpi', 'index', '--create', 'myindex', 'bases=/emilie/prod',
             'volatile=False', '--clientdir=/example'])

    def test_upload(self):
        dcw = DevpiCommandWrapper('http://localhost/', '/example')
        self.assertEqual(
            dcw.upload('/foo/bar/', directory=True),
            ['devpi', 'upload', '--from-dir',
             '/foo/bar/', '--clientdir=/example'])
        self.assertEqual(
            dcw.upload('/foo/bar/', dry_run=True),
            ['devpi', 'upload', '--dry-run',
             '/foo/bar/', '--clientdir=/example'])
        self.assertEqual(
            dcw.upload('/foo/bar/', with_docs=True),
            ['devpi', 'upload', '--with-docs',
             '/foo/bar/', '--clientdir=/example'])

    def test_remove(self):
        dcw = DevpiCommandWrapper('http://localhost/', '/example')
        self.assertEqual(
            dcw.remove('foobar'),
            ['devpi', 'remove', '-y', 'foobar', '--clientdir=/example'])
