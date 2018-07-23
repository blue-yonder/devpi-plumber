UNRELEASED
----------

- Support for Python 3.2, 3.3, and 3.4 is no longer tested.
- Add new list_users and delete_user functions to DevpiCommandWrapper
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
