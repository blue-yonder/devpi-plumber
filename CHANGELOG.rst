UNRELEASED
----------

- Establish compatibility with Devpi Server 6. Compatibility with Devpi Server < 5.2.0 is dropped for this.
- Add official support for Python 3.7 to 3.9.
- Drop support for Python 2.7 and 3.5.

0.5.1
-----

- Improve compatibility with Devpi 5.x by not processing events during state import.

0.5.0
-----

- Support for Python 3.2, 3.3, and 3.4 is no longer tested.
- Add new list_users, delete_user and delete_index functions to DevpiCommandWrapper
- Add DevpiCommandWrapper.user_session, a contextmanager which handles logon/logoff with supplied credentials

0.4.3
-----

- Fix compatibility with devpi-server 4.3.0 and up.
- The new environment variables ``DEVPI_PLUMBER_SERVER_HOST`` and ``DEVPI_PLUMBER_SERVER_PORT`` allow you to tune where
  the test server binds to from the outside.
- Add official support for Python 3.6.

0.4.2
-----
- Don't cache servers started with `--no-root-pypi`.

0.4.1
-----
- Fix bug in `import_state`.

0.4.0
-----
- Adapt for compatibility with devpi>=4.2.1 . This breaks compatibility with devpi<4.2.1 .
