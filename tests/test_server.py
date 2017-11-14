"""
Smoke tests that the provided TestServer works as expected.
"""

import mock
import pytest
import requests
from twitter.common.contextutil import temporary_dir

from devpi_plumber.server import TestServer, export_state, import_state


def test_server_start():
    with TestServer() as devpi:
        assert 200 == requests.get(devpi.url).status_code


def test_user_creation():
    users = {
        'user1': {'password': 'secret1'},
        'user2': {'password': 'secret2'},
    }
    with TestServer(users) as devpi:
        assert 200 == requests.get(devpi.url + '/user1').status_code
        assert 200 == requests.get(devpi.url + '/user2').status_code
        assert 404 == requests.get(devpi.url + '/user3').status_code


def test_index_creation():
    users = {
        'user1': {'password': 'secret1'},
    }
    indices = {
        'user1/index1': {},
        'user1/index2': {},
    }
    with TestServer(users, indices) as devpi:
        assert 200 == requests.get(devpi.url + '/user1/index1').status_code
        assert 200 == requests.get(devpi.url + '/user1/index2').status_code
        assert 404 == requests.get(devpi.url + '/user1/index3').status_code


def test_logwatch():
    with pytest.raises(RuntimeError):
        with TestServer(fail_on_output=['ERROR']) as devpi:
            assert 404 == requests.get(devpi.url + '/doesnt/exist').status_code


def test_import_export():
    users = {
        'user1': {'password': 'secret'},
    }

    with temporary_dir() as state_dir:
        with temporary_dir() as server_dir1:
            with TestServer(config=dict(serverdir=server_dir1), users=users) as devpi:
                assert 200 == requests.get(devpi.url + '/user1').status_code
            export_state(server_dir1, state_dir)

        with temporary_dir() as server_dir2:
            import_state(server_dir2, state_dir)
            with TestServer(config=dict(serverdir=server_dir2)) as devpi:
                assert 200 == requests.get(devpi.url + '/user1').status_code


def test_no_root_pypi_not_cached():
    # Work on separate cache -- must be empty for this test.
    import devpi_plumber.server
    with temporary_dir() as cache_dir:
        with mock.patch.object(devpi_plumber.server, 'serverdir_cache', new=cache_dir):
            with TestServer() as devpi:
                pass

            with TestServer(config={'no-root-pypi': None}):
                assert 404 == requests.get(devpi.url + '/root/pypi').status_code

            with TestServer() as devpi:
                assert 200 == requests.get(devpi.url + '/root/pypi').status_code


def test_log_printed_on_startup_failure(capsys):
    with pytest.raises(Exception):
        with TestServer(config={'foo': 'bla'}):  # use an invalid config to fail the start-up
            pass
    out, _ = capsys.readouterr()
    assert 'unrecognized argument' in out
