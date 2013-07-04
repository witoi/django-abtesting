#!/usr/bin/env python
from setuptools import setup


setup(name='django-abtesting',
      version='0.1',
      description='A/B testing library for Django',
      author='Pedro Buron',
      author_email='pedro@witoi.com',
      url='http://github.com/witoi/django-abtesting',
      packages=['abtesting', 'abtesting.templatetags'],
      package_data={'abtesting': ['templates/*.html', 'templates/*/*.html']}
)
