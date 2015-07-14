=======================
Mario the Devpi Plumber
=======================

.. image:: https://travis-ci.org/blue-yonder/devpi-plumber.svg?branch=master
    :alt: Build Status
    :target: https://travis-ci.org/blue-yonder/devpi-plumber 
.. image:: https://coveralls.io/repos/blue-yonder/devpi-plumber/badge.svg?branch=master
    :alt: Coverage Status
    :target: https://coveralls.io/r/blue-yonder/devpi-plumber?branch=master
.. image:: https://badge.fury.io/py/devpi-plumber.svg
    :alt: Latest Version
    :target: https://pypi.python.org/pypi/devpi-plumber
.. image:: https://requires.io/github/blue-yonder/devpi-plumber/requirements.svg?branch=master
    :alt: Requirements Status
    :target: https://requires.io/github/blue-yonder/devpi-plumber/requirements/?branch=master

Mario, the devpi-plumber, helps to automate and test large devpi_ installations. It offers a simple python commandline wrapper
around the devpi client binary and utilities for using devpi in a test harness.


Mario by Example:
=================

Among others, it can be used to automate the upload of packages:

.. code:: python

    with DevpiClient('https://devpi.company.com', 'user', 'secret') as devpi:
        devpi.use('user/testindex')
        devpi.upload('path_to_package')

In order to simplify the testing of such plumbing scripts, it ships with a simple context manager for starting and stopping devpi servers in tests

.. code:: python

    users = { 
        'user': {'password': 'secret'},
    }
    indices = {
        'user/prodindex': { },
        'user/testindex': {'bases': 'user/prodindex'},
    }
    with TestServer(users, indices) as devpi:
        devpi.use('user/testindex')
        devpi.upload('path_to_package')


License
=======

`New BSD`_


.. _devpi: http://doc.devpi.net/latest/
.. _New BSD: https://github.com/blue-yonder/devpi-builder/blob/master/COPYING
