# encoding=utf-8
from setuptools import find_packages, setup

setup(
    name='test-package',
    version='0.1',
    packages=find_packages(exclude=['tests']),
)
