=======================
Mario the Devpi Plumber
=======================

.. image:: https://coveralls.io/repos/blue-yonder/devpi-plumber/badge.svg?branch=master
    :alt: Coverage Status
    :target: https://coveralls.io/r/blue-yonder/devpi-plumber?branch=master
.. image:: https://badge.fury.io/py/devpi-plumber.svg
    :alt: Latest Version
    :target: https://pypi.python.org/pypi/devpi-plumber

Mario, the devpi-plumber, helps to automate and test large devpi_ installations. It offers a simple python commandline wrapper
around the devpi client binary and utilities for using devpi in a test harness. To get access to the latter, install Mario
with the extra ``test`` requirement::

    pip install devpi-plumber[test]


Mario by Example:
=================

Among others, it can be used to automate the upload of packages:

.. code:: python

    with DevpiClient('https://devpi.company.com', 'user', 'secret') as devpi:
        devpi.use('user/testindex')
        devpi.upload('path/to/package-1.0.tar.gz')

To make it easier to perform modifications on non-volatile indices, there is a context manager that temporarily toggles the volatile flag.

.. code:: python

    with volatile_index(devpi, 'user/prodindex'):
        devpi.remove('broken_package==0.1.0')

In order to simplify the testing of such plumbing scripts, it ships with a simple context manager for starting and stopping devpi servers in tests.

.. code:: python

    def do_maintenance(devpi):
        """ My plumbing script """
        devpi.use('user/testindex')
        # ...

    users = { 
        'user': {'password': 'secret'},
    }
    indices = {
        'user/prodindex': {},
        'user/testindex': {'bases': 'user/prodindex'},
    }
    with TestServer(users, indices) as devpi:
        do_maintenance(devpi)


License
=======

`New BSD`_


.. _devpi: http://doc.devpi.net/latest/
.. _New BSD: https://github.com/blue-yonder/devpi-builder/blob/master/COPYING
