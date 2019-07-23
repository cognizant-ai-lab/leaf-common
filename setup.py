import os
import sys

from setuptools import setup

CURRENT_PYTHON = sys.version_info[:2]
REQUIRED_PYTHON = (3, 6)

if CURRENT_PYTHON < REQUIRED_PYTHON:
    sys.stderr.write("""
==========================
Unsupported Python version
==========================
This version of esp-sdk requires Python {}.{}, but you're trying to
install it on Python {}.{}.
""".format(*(REQUIRED_PYTHON + CURRENT_PYTHON)))
    sys.exit(1)


def read(fname):
    with open(os.path.join(os.path.dirname(__file__), fname)) as f:
        return f.read()


setup(
    name='leaf-common',
    version='1.0.0',
    python_requires='>={}.{}'.format(*REQUIRED_PYTHON),
    packages=['grpc', 'logging'],
    install_requires=[
    ],
    description='LEAF team common code library',
    long_description=read('README.md'),
    author='Darren Sargent',
    url='https://github.com/leaf-ai/leaf-common/'
)
