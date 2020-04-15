from setuptools import setup
from multiloan import __version__

dependencies = ['numpy', 'pandas']

with open('README.md') as fh:
    long_description = fh.read()

setup(
    name='multiloan',
    version=__version__,
    packages=['multiloan'],
    install_requires=dependencies,
    url='',
    license='MIT',
    author='michaelsilverstein',
    author_email='michael.silverstein4@gmail.com',
    description='Tools for managing loan payments',
    long_description = long_description,
    long_description_content_type = "text/markdown",
)
