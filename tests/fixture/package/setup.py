# encoding=utf-8
from setuptools import setup, find_packages

setup(
    name='test-package',
    version='0.1',
    packages=find_packages(exclude=['tests']),
    url='http://blue-yonder.com',
    author='Blue Yonder GmbH',
    author_email='someone@domain.invalid',
)
