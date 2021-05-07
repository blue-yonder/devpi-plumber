# coding=utf-8

import multiprocessing  # avoid crash on teardown
from setuptools import setup, find_packages

with open('README.rst') as f:
    readme = f.read()

setup(
    name='devpi-plumber',
    use_scm_version=True,
    packages=find_packages(exclude=['tests']),
    author='Stephan Erb',
    author_email='stephan.erb@blue-yonder.com',
    url='https://github.com/blue-yonder/devpi-plumber',
    description='Mario, the devpi-plumber, helps to automate and test large devpi installations.',
    long_description=readme,
    license='new BSD',
    setup_requires=[
        'setuptools_scm',
    ],
    install_requires=[
        'devpi-client',
        'requests',
        'twitter.common.contextutil',
    ],
    extras_require={
        'test': ['devpi-server>=4.2.1'],
    },
    tests_require=[
        'mock',
        'pytest',
        'pytest-cov',
    ],
    classifiers=[
        'Development Status :: 4 - Beta',
        'Environment :: Console',
        'Intended Audience :: Developers',
        'Intended Audience :: System Administrators',
        'License :: OSI Approved :: BSD License',
        'Topic :: System :: Archiving :: Packaging',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
    ],
)
