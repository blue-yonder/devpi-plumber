import os
import shutil
import atexit
import contextlib
import subprocess

from six import iteritems
from twitter.common.contextutil import temporary_dir

from devpi_plumber.client import DevpiClient


@contextlib.contextmanager
def TestServer(users={}, indices={}, config={}, fail_on_output=['Traceback']):
    """
    Starts a devpi server to be used within tests.
    """
    with temporary_dir() as server_dir:

        server_options = {
            'port' : 2414,
            'serverdir' : server_dir}
        server_options.update(config)

        prefill_serverdir(server_options)

        with DevpiServer(server_options) as url:
            with DevpiClient(url, 'root', '') as client:

                for user, kwargs in iteritems(users):
                    client.create_user(user, **kwargs)

                for index, kwargs in iteritems(indices):
                    client.create_index(index, **kwargs)

                yield client

            with open(server_dir + '/.xproc/devpi-server/xprocess.log') as f:
                logs = f.read()
                if any((message in logs) for message in fail_on_output):
                    raise RuntimeError(logs)


@contextlib.contextmanager
def DevpiServer(options):
        args = ['--{}={}'.format(k, v) for k, v in iteritems(options)]
        subprocess.check_output(['devpi-server', '--start'] + args, stderr=subprocess.STDOUT)
        try:
            yield 'http://localhost:{}'.format(options['port'])
        finally:
            subprocess.check_output(['devpi-server', '--stop'] + args, stderr=subprocess.STDOUT)


serverdir_cache = '/tmp/devpi-plumber-cache'
atexit.register(shutil.rmtree, serverdir_cache, ignore_errors=True)


def prefill_serverdir(server_options):
    """
    Starting a new devpi-server is costly due to its initial sync with pypi.python.org.
    We can speedup this process by using the content of a cached serverdir.
    """
    serverdir_new = server_options['serverdir']

    if 'master-url' in server_options:
        return  # always has to be a fresh sync
    elif os.path.exists(serverdir_cache):
        shutil.rmtree(serverdir_new)
        shutil.copytree(serverdir_cache, serverdir_new)
    else:
        with DevpiServer(server_options):
            shutil.copytree(serverdir_new, serverdir_cache)
