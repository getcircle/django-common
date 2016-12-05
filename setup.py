from setuptools import (
    find_packages,
    setup,
)

import common

setup(
    name='django-common',
    version=common.__version__,
    description='Common django utilities',
    packages=find_packages(),
    install_requires=['django>=1.7.1'],
)
