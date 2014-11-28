# coding=utf-8

import multiprocessing  # avoid crash on teardown
from setuptools import setup, find_packages

with open('README.md') as f:
    readme = f.read()

setup(
    name='devpi-plumber',
    version='0.2.1',
    packages=find_packages(exclude=['tests']),
    author='Stephan Erb',
    author_email='stephan.erb@blue-yonder.com',
    url='https://github.com/blue-yonder/devpi-plumber',
    description='Mario, the devpi-plumber, helps to automate and test large devpi installations.',
    long_description=readme,
    license='new BSD',
    install_requires=[
        'devpi-client',
        'devpi-server',
        'twitter.common.contextutil',
        'six'
    ],
    setup_requires=[
        'nose'
    ],
    tests_require=[
        'nose',
        'nose-progressive',
        'mock',
        'coverage',
    ],
    test_suite='nose.collector',
    classifiers=[
        'Development Status :: 4 - Beta',
        'Environment :: Console',
        'Intended Audience :: Developers',
        'Intended Audience :: System Administrators',
        'License :: OSI Approved :: BSD License',
        'Topic :: System :: Archiving :: Packaging',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.2',
        'Programming Language :: Python :: 3.3',
        'Programming Language :: Python :: 3.4',
    ],
)
