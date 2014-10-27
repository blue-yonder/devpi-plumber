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
        self._devpi('use', self._index_url)
        if self._user and self._password is not None:
            self._devpi('login', self._user, '--password', self._password)
        return self

    def __exit__(self, *args):
        shutil.rmtree(self._client_dir)

    @property
    def index_url(self):
        return self._index_url


    def _devpi(self, *args):
        return subprocess.check_output(
            ['devpi'] + list(args) + ['--clientdir={}'.format(self._client_dir)],
            stderr=subprocess.STDOUT
        )

    def list_packages(self, package_filter=""):
        """
        List packages on the index associated to this client.

        :param package_filter: optional query filter, such as 'mypackage' or 'mypackage>=version'
        """
        return self._devpi('list', package_filter)

    def list_indices(self):
        return [ line.split()[0] for line in self._devpi('use', '-l').splitlines() ]

    def upload(self, file):
        """
        Upload the given file to the current index
        """
        self._devpi('upload', file)

