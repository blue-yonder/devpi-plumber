import atexit
import contextlib
import os
import shutil
import subprocess
import time

import requests

from devpi_plumber.client import DevpiClient
from six import iteritems
from twitter.common.contextutil import temporary_dir


@contextlib.contextmanager
def TestServer(users={}, indices={}, config={}, fail_on_output=['Traceback']):
    """
    Starts a devpi server to be used within tests.
    """
    with temporary_dir() as server_dir:

        server_options = {
            'host': os.getenv('DEVPI_PLUMBER_SERVER_HOST', 'localhost'),
            'port': os.getenv('DEVPI_PLUMBER_SERVER_PORT', 2414),
            'serverdir': server_dir,
        }
        server_options.update(config)

        initialize_serverdir(server_options)

        with DevpiServer(server_options) as url:
            with DevpiClient(url, 'root', '') as client:

                for user, kwargs in iteritems(users):
                    client.create_user(user, **kwargs)

                for index, kwargs in iteritems(indices):
                    client.create_index(index, **kwargs)

                yield client

        _assert_no_logged_errors(fail_on_output, server_options['serverdir'] + '/server.log')


def import_state(serverdir, importdir):
    devpi_server_command(serverdir=serverdir, init=None)
    devpi_server_command(serverdir=serverdir, **{'import': importdir})


def export_state(serverdir, exportdir):
    devpi_server_command(serverdir=serverdir, export=exportdir)


def _assert_no_logged_errors(fail_on_output, logfile):
    with open(logfile) as f:
        logs = f.read()
    for message in fail_on_output:
        if message not in logs:
            continue
        if message == 'Traceback' and logs.count(message) == logs.count('ValueError: I/O operation on closed file'):
            # Heuristic to ignore false positives on the shutdown of replicas
            # The master might still be busy serving root/pypi/simple for a stopping replica
            continue
        raise RuntimeError(logs)


@contextlib.contextmanager
def DevpiServer(options):
    url = 'http://localhost:{}'.format(options['port'])
    server = None
    logfile = options['serverdir'] + '/server.log' if 'serverdir' in options else os.devnull
    with open(logfile, 'wb', buffering=0) as stdout:
        try:
            server = subprocess.Popen(
                build_devpi_server_command(**options),
                stderr=subprocess.STDOUT,
                stdout=stdout,
            )
            wait_for_startup(server, url)
            yield url
        finally:
            if server:
                server.terminate()
                try:
                    server.wait(30)
                except TimeoutError:
                    server.kill()
                    server.wait(30)


def build_devpi_server_command(**options):
    opts = ['--{}={}'.format(k, v) for k, v in iteritems(options) if v is not None]
    flags = ['--{}'.format(k) for k, v in iteritems(options) if v is None]
    return ['devpi-server'] + opts + flags


def devpi_server_command(**options):
    subprocess.check_output(build_devpi_server_command(**options), stderr=subprocess.STDOUT)


def wait_for_startup(server, url):
    deadline = time.time() + 30
    while time.time() < deadline:
        if server.poll() is not None:
            raise Exception('Server failed to start up.')
        try:
            requests.get(url, timeout=0.1)
        except requests.RequestException:
            time.sleep(0.1)  # Request failed, try again
        else:
            return  # Server came up
    raise Exception('Server failed to start up within 30 seconds.')



serverdir_cache = '/tmp/devpi-plumber-cache'
atexit.register(shutil.rmtree, serverdir_cache, ignore_errors=True)


def initialize_serverdir(server_options):
    """
    Starting a new devpi-server is costly due to its initial sync with pypi.python.org.
    We can speedup this process by using the content of a cached serverdir.
    """
    def init_serverdir():
        devpi_server_command(init=None, **server_options)

    serverdir_new = server_options['serverdir']

    if os.path.exists(serverdir_new) and os.listdir(serverdir_new):
        # Don't touch already populated directory.
        return

    if 'no-root-pypi' in server_options:
        # Always run servers called with `--no-root-pypi in a freshly initialized serverdir.
        init_serverdir()
        return

    if 'master-url' in server_options:
        # Running as replica. Aways has to be a fresh sync.
        init_serverdir()
    else:
        # Running as master.
        if os.path.exists(serverdir_cache) and os.listdir(serverdir_cache):
            shutil.rmtree(serverdir_new)
            shutil.copytree(serverdir_cache, serverdir_new)
        else:
            init_serverdir()
            shutil.rmtree(serverdir_cache, ignore_errors=True)
            shutil.copytree(serverdir_new, serverdir_cache)
