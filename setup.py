"""
Installation script for leaf-common library
"""

import os
import sys

from setuptools import setup, find_packages

LIBRARY_VERSION = "1.1.49"

CURRENT_PYTHON = sys.version_info[:2]
REQUIRED_PYTHON = (3, 6)

if CURRENT_PYTHON < REQUIRED_PYTHON:
    # pylint: disable=consider-using-f-string
    sys.stderr.write("""
==========================
Unsupported Python version
==========================
This version of leaf-common requires Python {}.{}, but you're trying to
install it on Python {}.{}.
""".format(*(REQUIRED_PYTHON + CURRENT_PYTHON)))
    sys.exit(1)


def _read(fname):
    with open(os.path.join(os.path.dirname(__file__), fname), encoding="UTF-8") as file_name:
        return file_name.read()


setup(
    name='leaf-common',
    version=LIBRARY_VERSION,
    python_requires='>={}.{}'.format(*REQUIRED_PYTHON),     # pylint: disable=consider-using-f-string
    packages=find_packages('.', exclude=['tests*']),
    install_requires=[
        # Specifically use >= to specify a base version we know works
        # while allowing code that depends on this library to upgrade
        # versions as they see fit.
        "Deprecated>=1.2.13",
        "grpcio>=1.38.1",
        "hvac>=0.11.2",
        "pyhocon>=0.3.59",
        "pyOpenSSL>=21.0.0",
        "python-jose>=3.3.0",
        "pytz>=2021.3",
        "ruamel.yaml>=0.17.20"
    ],
    description='LEAF team common code library',
    long_description=_read('README.md'),
    author='Dan Fink',
    url='https://github.com/leaf-ai/leaf-common/'
)
