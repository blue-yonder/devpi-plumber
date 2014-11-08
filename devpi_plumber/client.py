import sys
import tempfile
import shutil
import logging
from cStringIO import StringIO

from devpi.main import main as devpi
from twitter.common.contextutil import mutable_sys


logging.getLogger("requests").setLevel(logging.WARNING)
logging.getLogger("devpi").setLevel(logging.WARNING)


class DevpiClientException(Exception):
    """
    Exception thrown whenever a client command fails
    """


class DevpiClient(object):
    """
    Light wrapper object around the devpi client.
    """
    def __init__(self, url, user=None, password=None):
        self._url = url
        self._user = user
        self._password = password

    def __enter__(self):
        self._client_dir = tempfile.mkdtemp()
        try:
            self.use()
            if self._user and self._password is not None:
                self.login(self._user, self._password)
            return self
        except:
            self.__exit__()
            raise

    def __exit__(self, *args):
        shutil.rmtree(self._client_dir)

    @property
    def url(self):
        return self._url

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
