from setuptools import setup, find_packages
import sys, os

version = '2.0'

setup(name='Catwalk',
      version=version,
      description="A way to view your models usingg TurboGears",
      long_description="""\
""",
      classifiers=[], # Get strings from http://pypi.python.org/pypi?%3Aaction=list_classifiers
      keywords='sqlalchemy, TurboGears, DBSprockets',
      author='Christopher Perkins',
      author_email='chris@percious.com',
      url='http://code.google.com/p/tgtools/wiki/Catwalk',
      license='MIT',
      packages=find_packages(exclude=['ez_setup', 'examples', 'tests']),
      include_package_data=True,
      zip_safe=True,
      install_requires=[
        'sprox>=0.5b1'  
	# -*- Extra requirements: -*-
      ],
      entry_points="""
      # -*- Entry points: -*-
      """,
      )
