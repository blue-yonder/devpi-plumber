import subprocess
import tempfile
import shutil


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
        self.use()
        if self._user and self._password is not None:
            self.login(self._user, self._password)
        return self

    def __exit__(self, *args):
        shutil.rmtree(self._client_dir)

    @property
    def url(self):
        return self._url

    def execute(self, *args, **kwargs):
        try:
            return subprocess.check_output(
                ['devpi'] + list(args)
                          + ['{}={}'.format(k, v) for k,v in kwargs.iteritems()]
                          + ['--clientdir={}'.format(self._client_dir)],
                stderr=subprocess.STDOUT
            )
        except subprocess.CalledProcessError as e:
            raise RuntimeError("Devpi command failed: " + e.output + str(e))

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
