from setuptools import setup
from multiloan import __version__

dependencies = ['numpy', 'pandas']

setup(
    name='multiloan',
    version=__version__,
    packages=['multiloan'],
    install_requires=dependencies,
    url='',
    license='',
    author='michaelsilverstein',
    author_email='michael.silverstein4@gmail.com',
    description='Tools for managing loan payments'
)
