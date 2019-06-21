# -*- coding: utf-8 -*-

from setuptools import setup, find_packages


with open('LICENSE.txt') as f:
    license = f.read()

setup(
    name='c2dh-nerd',
    version='0.1.0',
    description='Named entity recognition and disambiguation',
    long_description='Uni.lu C2DH named entity recognition and disambiguation',
    author='Roman Kalyakin',
    author_email='roman@kalyakin.com',
    url='',
    license=license,
    packages=find_packages(exclude=('tests'))
)
