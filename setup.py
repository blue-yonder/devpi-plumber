# coding=utf-8

import multiprocessing  # avoid crash on teardown
from setuptools import setup, find_packages

with open('README.rst') as f:
    readme = f.read()
with open('core-requirements.txt') as f:
    requirements = [line.strip() for line in f.readlines() if line[:1] != '#']
with open('extra-test-requirements.txt') as f:
    extra_test_requirements = [line.strip() for line in f.readlines() if line[:1] != '#']


setup(
    name='devpi-plumber',
    use_scm_version=True,
    packages=find_packages(exclude=['tests']),
    author='Stephan Erb',
    author_email='stephan.erb@blue-yonder.com',
    url='https://github.com/blue-yonder/devpi-plumber',
    description='Mario, the devpi-plumber, helps to automate and test large devpi installations.',
    long_description=readme,
    long_description_content_type='text/x-rst',
    license='new BSD',
    setup_requires=[
        'setuptools_scm',
    ],
    install_requires=requirements,
    extras_require={
        'test': extra_test_requirements,
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
        'Programming Language :: Python :: 3.9',
        'Programming Language :: Python :: 3.10',
        'Programming Language :: Python :: 3.11',
        'Programming Language :: Python :: 3.12',
    ],
)
