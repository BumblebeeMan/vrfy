#!/usr/bin/env python3

from setuptools import setup
import setuptools

with open("README.md", "r", encoding='utf-8') as file:
    long_description = file.read()

setup(
    name = 'vrfy',
    version = '0.1.0',
    description = 'Tool to verify the content of (copied) directories.',
    long_description = long_description,
    long_description_content_type='text/markdown',

    py_modules = ["vrfy"],
    package_dir = {'': 'src'},

    author="BumblebeeMan (Dennis Koerner)", 
    author_email="dennis@bumblebeeman.dev",     
    url="https://github.com/BumblebeeMan/vrfy",

    #install_requires=["requests >= 2.30.0", "psutil >= 5.9.0"],

    python_requires=">=3.7",

    keywords=["vrfy", "verify", "check", "directory", "hash"],

    classifiers=["Development Status :: 4 - Beta",
                 "License :: OSI Approved :: GNU General Public License v3 (GPLv3)",
                 "Operating System :: OS Independent",
                 "Programming Language :: Python :: 3",
                 "Programming Language :: Python :: 3 :: Only",
                 "Programming Language :: Python :: 3.7",
                 "Programming Language :: Python :: 3.8",
                 "Programming Language :: Python :: 3.9",
                 "Programming Language :: Python :: 3.10",
                 "Programming Language :: Python :: 3.11",
                 ]  
)
