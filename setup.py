from setuptools import setup, find_packages
import sys, os

version = '2.0.2'

setup(name='Catwalk',
      version=version,
      description="A way to view your models using TurboGears",
      long_description="""""",
      classifiers=[], 
      keywords='sqlalchemy, TurboGears, Sprox, tgext.admin',
      author='Christopher Perkins',
      author_email='chris@percious.com',
      url='http://code.google.com/p/tgtools/wiki/Catwalk',
      license='MIT',
      packages=find_packages(exclude=['ez_setup', 'examples', 'tests']),
      include_package_data=True,
      zip_safe=False,
      install_requires=[
        'sprox',
        'tgext.admin',
      ],
      )
