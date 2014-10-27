import contextlib
import shutil
import subprocess
import tempfile

from devpi_plumber.client import DevpiClient


@contextlib.contextmanager
def devpi_server(port=2414, options=[]):
    server_dir = tempfile.mkdtemp()
    try:
        subprocess.check_output(['devpi-server', '--start', '--serverdir={}'.format(server_dir), '--port={}'.format(port)] + options, stderr=subprocess.STDOUT)
        try:
            yield 'http://localhost:{}'.format(port)
        finally:
            subprocess.check_output(['devpi-server', '--stop', '--serverdir={}'.format(server_dir)] + options, stderr=subprocess.STDOUT)
    finally:
        shutil.rmtree(server_dir)


@contextlib.contextmanager
def devpi_user(server_url, user, password=""):
    """
    Creates the giver user, and deletes it afterwards
    """
    with DevpiClient(server_url) as devpi_client:
        devpi_client.execute('user', '-c', user, 'password=' + password)
        try:
            yield '{}/{}'.format(server_url, user)
        finally:
            devpi_client.execute('login', user, '--password', password)
            devpi_client.execute('user', user, '--delete')


@contextlib.contextmanager
def devpi_index(server_url, user, index, password="", **kwargs):
    """
    Creates the given index for the given user drop it afterwards.
    """
    with DevpiClient(server_url, user, password) as devpi_client:
        print devpi_client.execute('index', '-c', index, 'bases=', **kwargs)
        try:
            yield '{}/{}/{}'.format(server_url, user, index)
        finally:
            devpi_client.execute('index', '--delete', '/{}/{}'.format(user, index))


