from setuptools import setup

import common

setup(
    name='django-common',
    version=common.__version__,
    description='Common django utilities',
    py_modules=['common'],
)
