# -*- coding: utf-8 -*-

# Learn more: https://github.com/kennethreitz/setup.py

from setuptools import setup, find_packages


with open('README.rst') as f:
    readme = f.read()

with open('LICENSE') as f:
    license = f.read()

setup(
    name='crypto-tensor',
    version='0.1.0',
    description='Package for Crypto-Tensor bot',
    long_description=readme,
    author='Dennis Thiessen',
    author_email='dennis.thiessen@riskahead.de',
    url='https://gitlab.riskahead.de/root/crypto-prediction',
    license=license,
    packages=find_packages(exclude=('tests', 'docs'))
)

