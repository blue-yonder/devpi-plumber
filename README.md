Mario the Devpi Plumber
=======================

Mario, the devpi-plumber, helps to automate and test large devpi installations. It offers a simple python commandline wrapper
around the devpi client binary and utilities for using devpi in a test harness.


Mario by Example:
-----------------
Among others, it can be used to automate the upload of packages:
```python
with DevpiClient('http://devpi.company.com', 'user', 'password') as devpi:
    devpi.use('user/test')
    devpi.upload('path_to_package')
```

In order to simplify the testing of such plumbing scripts, it ships with a simple context manager for starting and stopping devpi servers in tests:
```python
users = { 
    'user': {'password': 'secret'}
}
indices = {
    'user/prod': {},
    'user/test': {bases:'user/prod'},
}
with TestServer(users, indices) as devpi:
    devpi.use('user/test')
    devpi.upload('path_to_package')
```           

License
-------

[New BSD](COPYING)
