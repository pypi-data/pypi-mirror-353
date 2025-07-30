# -*- coding: utf-8 -*-
from setuptools import setup, find_packages
LONGDOC = """
langchain_chatopera
=====================

build Agent Services by integrating chatopera cloud services with langchain via tool calling

https://github.com/chatopera/langchain-chatopera

"""

setup(
    name='langchain_chatopera',
    version='0.0.1',
    description='build Agent Services by integrating chatopera cloud services with langchain via tool calling',
    long_description=LONGDOC,
    author='Chatopera DevOps Team',
    author_email='info@chatopera.com',
    url='https://github.com/chatopera/langchain-chatopera',
    license="Apache License, version 2.0",
    classifiers=[
        'Intended Audience :: Developers',
        'Operating System :: OS Independent',
        'Natural Language :: Chinese (Simplified)',
        'Natural Language :: Chinese (Traditional)',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.11'
    ],
    keywords='agent,chatbot,AI,NLP',
    packages=find_packages(),
    install_requires=[
        'langchain>=0.3.0',
        'pydantic>=2.0.0',
        'chatopera>=2.0.0'
    ],
    package_data={
        'langchain-chatopera': [
            'LICENSE']})
