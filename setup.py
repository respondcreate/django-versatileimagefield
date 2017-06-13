# -*- coding: utf-8 -*-
from distutils.core import setup
from setuptools import find_packages

setup(
    name='django-versatileimagefield',
    packages=find_packages(),
    version='1.7.1',
    author=u'Jonathan Ellenberger',
    author_email='jonathan_ellenberger@wgbh.org',
    url='http://github.com/respondcreate/django-versatileimagefield/',
    license='MIT License, see LICENSE',
    description="A drop-in replacement for django's ImageField that provides "
                "a flexible, intuitive and easily-extensible interface for "
                "creating new images from the one assigned to the field.",
    long_description=open('README.rst').read(),
    zip_safe=False,
    install_requires=['Pillow>=2.4.0,<=4.0.0'],
    include_package_data=True,
    keywords=[
        'django',
    ],
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Environment :: Web Environment',
        'Framework :: Django',
        'Framework :: Django :: 1.8',
        'Framework :: Django :: 1.9',
        'Framework :: Django :: 1.10',
        'Framework :: Django :: 1.11',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Natural Language :: English',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Topic :: Multimedia :: Graphics :: Presentation',
    ]
)
