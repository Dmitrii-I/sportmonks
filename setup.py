"""Configure package installation and distribution."""

from setuptools import setup, find_packages
from sportmonks_v2 import __version__

setup_args = dict(
    name='sportmonks_v2',
    version=__version__,
    description='Pythonic wrapper around SportMonks API.',
    long_description='Pythonic wrapper around SportMonks API.',
    author='Sebastiaan Speck',
    author_email='shemspeck@gmail.com',
    url='https://github.com/sebastiaanspeck/sportmonks_v2',
    download_url='https://pypi.org/project/sportmonks_v2/',
    license='MIT',
    packages=find_packages(exclude=['contrib', 'docs', '*test*']),
    install_requires=['requests'],
    python_requires='>=3.5.2',
)

if __name__ == '__main__':
    setup(**setup_args)
