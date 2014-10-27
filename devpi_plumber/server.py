import contextlib
import shutil
import subprocess
import tempfile

from devpi_plumber.client import DevpiClient


@contextlib.contextmanager
def DevpiServer(port=2414):
    server_dir = tempfile.mkdtemp()
    try:
        subprocess.check_output(['devpi-server', '--start', '--serverdir={}'.format(server_dir), '--port={}'.format(port)], stderr=subprocess.STDOUT)
        try:
            yield 'http://localhost:{}'.format(port)
        finally:
            subprocess.check_output(['devpi-server', '--stop', '--serverdir={}'.format(server_dir)], stderr=subprocess.STDOUT)
    finally:
        shutil.rmtree(server_dir)


@contextlib.contextmanager
def DevpiUser(server_url, user, password='dummy.password'):
    """
    Creates the giver user, and deletes it afterwards
    """
    with DevpiClient(server_url) as devpi_client:
        devpi_client._devpi('user', '-c', user, 'password=' + password)
        try:
            yield user, password
        finally:
            devpi_client._devpi('user', user, '--delete')


@contextlib.contextmanager
def DevpiIndex(server_url, user, index, password=None):
    """
    Creates the given index, and drops it afterwards.
    """
    with DevpiClient(server_url) as devpi_client:
        devpi_client._devpi('login', user, '--password=' + password)
        devpi_client._devpi('index', '-c', index, 'bases=')
        try:
            yield '{}/{}/{}'.format(server_url, user, index), password
        finally:
            devpi_client._devpi('index', '--delete', '/{}/{}'.format(user, index))


