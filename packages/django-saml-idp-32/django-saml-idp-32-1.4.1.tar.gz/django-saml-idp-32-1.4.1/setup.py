# -*- coding: utf-8 -*-
from setuptools import setup, find_packages
import saml2idp


with open('README.md') as readme:
    description = readme.read()


with open('HISTORY.md') as history:
    changelog = history.read()


setup(
    name='django-saml-idp-32',
    version=saml2idp.__version__,
    author='Gabriel de Forest, Brian Tiemann, Sebastian Vetter',
    author_email='sebastian@mobify.com',
    maintainer='Ceejay Guiking',
    maintainer_email='ceejay.guiking@mpulse.com',
    description='SAML 2.0 IdP for Django (patched fork for Django 3.2+ compatibility)',
    long_description='\n\n'.join([description, changelog]),
    long_description_content_type='text/markdown',
    install_requires=[
        'Django>=3.2',
        'M2Crypto>=0.38.0',
        'beautifulsoup4>=4.7.1',
        'structlog',
        'six',
    ],
    license='MIT',
    packages=find_packages(exclude=['idptest*']),
    url='https://github.com/sessions8934/dj-saml-idp',
    zip_safe=False,
    include_package_data=True,
)
