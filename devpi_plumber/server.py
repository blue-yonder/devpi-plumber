import atexit
import contextlib
import os
import shutil
import subprocess

from devpi_plumber.client import DevpiClient
from six import iteritems
from twitter.common.contextutil import temporary_dir


@contextlib.contextmanager
def TestServer(users={}, indices={}, config={}, fail_on_output=['Traceback'], serverdir=None):
    """
    Starts a devpi server to be used within tests.
    """
    server_options = {
        'port': 2414,
    }
    server_options.update(config)

    @contextlib.contextmanager
    def run_server(options):

        with DevpiServer(options) as url:
            with DevpiClient(url, 'root', '') as client:

                for user, kwargs in iteritems(users):
                    client.create_user(user, **kwargs)

                for index, kwargs in iteritems(indices):
                    client.create_index(index, **kwargs)

                yield client

        _assert_no_logged_errors(fail_on_output, options['serverdir'] + '/.xproc/devpi-server/xprocess.log')

    if not serverdir:
        with temporary_dir() as serverdir:
            server_options.update(serverdir=serverdir)
            prefill_serverdir(server_options)
            with run_server(server_options) as devpi:
                yield devpi
    else:
        server_options.update(serverdir=serverdir)
        with run_server(server_options) as devpi:
            yield devpi


def import_(serverdir, importdir):
    devpi_server_command(serverdir=serverdir, **{'import': importdir})


def export(serverdir, exportdir):
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
    try:
        devpi_server_command(start=None, **options)
        yield 'http://localhost:{}'.format(options['port'])
    finally:
        devpi_server_command(stop=None, **options)


def devpi_server_command(**options):
    opts = ['--{}={}'.format(k, v) for k, v in iteritems(options) if v is not None]
    flags = ['--{}'.format(k) for k, v in iteritems(options) if v is None]
    subprocess.check_output(['devpi-server'] + opts + flags, stderr=subprocess.STDOUT)


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
