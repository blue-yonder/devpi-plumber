import subprocess
import tempfile
import shutil


class DevpiClient(object):
    """
    Wrapper object around the devpi client exposing features required by devpi_builder.
    """
    def __init__(self, index_url, user=None, password=None):
        self._index_url = index_url
        self._user = user
        self._password = password

    def __enter__(self):
        self._client_dir = tempfile.mkdtemp()
        self.execute('use', self._index_url)
        if self._user and self._password is not None:
            self.execute('login', self._user, '--password', self._password)
        return self

    def __exit__(self, *args):
        shutil.rmtree(self._client_dir)

    @property
    def index_url(self):
        return self._index_url

    def execute(self, *args, **kwargs):
        try:
            return subprocess.check_output(
                ['devpi'] + list(args)
                          + ['{}={}'.format(key, value) for key,value in kwargs.iteritems()]
                          + ['--clientdir={}'.format(self._client_dir)],
                stderr=subprocess.STDOUT
            )
        except subprocess.CalledProcessError as e:
            raise RuntimeError("Devpi command failed: " + e.output)

    def login(self, user, password):
        return self.execute('login', user, '--password', password)
