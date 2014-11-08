import sys
import logging
import contextlib
from cStringIO import StringIO

from devpi.main import main as devpi
from twitter.common.contextutil import mutable_sys, temporary_dir


logging.getLogger("requests").setLevel(logging.WARNING)
logging.getLogger("devpi").setLevel(logging.WARNING)


class DevpiClientException(Exception):
    """
    Exception thrown whenever a client command fails
    """
    pass


@contextlib.contextmanager
def DevpiClient(url, user=None, password=None):
    """
    Yields a light wrapper object around the devpi client.
    """
    with temporary_dir() as client_dir:
        wrapper = DevpiCommandWrapper(url, client_dir)

        wrapper.use()
        if user and password is not None:
            wrapper.login(user, password)

        yield wrapper


class DevpiCommandWrapper(object):

    def __init__(self, url, client_dir):
        self._url = url
        self._client_dir = client_dir

    def execute(self, *args, **kwargs):
        keywordargs = { '--clientdir' : self._client_dir }
        keywordargs.update(kwargs)

        args = ['devpi'] + list(args) + ['{}={}'.format(k, v) for k,v in keywordargs.iteritems()]

        with mutable_sys():
            sys.stdout = sys.stderr = output = StringIO()
            try:
                devpi(args)
                return output.getvalue()
            except SystemExit:
                raise DevpiClientException(output.getvalue())

    def use(self, *args):
        return self.execute('use', '/'.join([self._url] + list(args)))

    def login(self, user, password):
        return self.execute('login', user, '--password', password)

    def logoff(self):
        return self.execute('logoff')

    def create_user(self, user, *args, **kwargs):
        return self.execute('user', '--create', user, *args, **kwargs)

    def create_index(self, index, *args, **kwargs):
        return self.execute('index', '--create', index, *args, **kwargs)

    def modify_user(self, user, *args, **kwargs):
        return self.execute('user', '--modify', user, *args, **kwargs)

    def modify_index(self, index, *args, **kwargs):
        return self.execute('index', index, *args, **kwargs)

    def upload(self, package, directory=False):
        args = "--from-dir" if directory else ""
        return self.execute("upload", args, package)

    @property
    def url(self):
        return self._url
