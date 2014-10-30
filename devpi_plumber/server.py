import contextlib
import subprocess

from twitter.common.contextutil import temporary_dir

from devpi_plumber.client import DevpiClient


@contextlib.contextmanager
def TestServer(users={}, indices={}, config={}):
    """
    Starts a devpi server to be used within tests.
    """
    with temporary_dir() as server_dir:

        server_options = {
            'port' : 2414,
            'serverdir' : server_dir}
        server_options.update(config)

        with DevpiServer(server_options) as url:
            with DevpiClient(url, 'root', '') as client:

                for user, kwargs in users.iteritems():
                    client.create_user(user, **kwargs)

                for index, kwargs in indices.iteritems():
                    client.create_index(index, **kwargs)

                yield client # Server is wiped on return. No need to cleanup users and indices


@contextlib.contextmanager
def DevpiServer(options):
        args = ['--{}={}'.format(k, v) for k,v in options.iteritems()]
        subprocess.check_output(['devpi-server', '--start'] + args, stderr=subprocess.STDOUT)
        try:
            yield 'http://localhost:{}'.format(options['port'])
        finally:
            subprocess.check_output(['devpi-server', '--stop'] + args, stderr=subprocess.STDOUT)
