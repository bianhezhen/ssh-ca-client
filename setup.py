"""
The setup module for cloudformation stack deployer
"""

# Always prefer setuptools over distutils
from setuptools import setup, find_packages
# To use a consistent encoding
from codecs import open
from os import path, environ
import subprocess

try:
    version = subprocess.check_output(['git', 'describe', '--tags']).decode('utf-8').rstrip()
except:
    version = '0.0.0'

here = path.abspath(path.dirname(__file__))

# Get the long description from the README file
with open(path.join(here, 'README.md'), encoding='utf-8') as f:
    long_description = f.read()

setup(
    name='ca-client',
    version=version,

    description='SSH CA Client',
    long_description=long_description,

    url='https://github.com/commercehub-oss/ssh-ca-client',
    author='CommerceHub',

    packages=find_packages(),

    classifiers=[
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3.2',
        'Programming Language :: Python :: 3.3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
    ],
    install_requires=[
        'argparse>=1.1',
        'requests>=2.13.0',
    ],

    entry_points={
        'console_scripts': [
            'ca-client=ssh_ca_client.cli:main'
        ]
    }
)
