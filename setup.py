import os
import sys

__version__ = '0.1'

if len(set(('test', 'easy_install')).intersection(sys.argv)) > 0:
    import setuptools

from distutils.core import setup

extra_setuptools_args = {}
if 'setuptools' in sys.modules:
    extra_setuptools_args = dict(
        tests_require=['nose'],
        test_suite='nose.collector',
        extras_require=dict(
            test='nose>=0.10.1')
    )

setup(name="nsweb",
      version=__version__,
      description="Neurosynth web app",
      maintainer='Tal Yarkoni',
      maintainer_email='tyarkoni@gmail.com',
      url='http://github.com/psychoinformaticslab/nsweb',
      packages=["nsweb","tests"],
      **extra_setuptools_args
      )
