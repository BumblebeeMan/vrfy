#!/usr/bin/env python3

from setuptools import setup
import setuptools

with open("README.md", "r", encoding='utf-8') as file:
    long_description = file.read()

setup(
    name='vrfy',
    version='0.4.0',
    description='Verify with VRFY: Ensure the integrity of your file copies, hash by hash!',
    long_description=long_description,
    long_description_content_type='text/markdown',

    packages=['vrfy', 'vrfy.cli'],

    author="BumblebeeMan (Dennis Koerner)",
    author_email="dennis@bumblebeeman.dev",
    url="https://github.com/BumblebeeMan/vrfy",

    entry_points={
        'console_scripts': [
            'vrfy = vrfy.cli.vrfyCli:main',
        ],
    },

    python_requires=">=3.7",

    keywords=["vrfy", "verify", "check", "directory", "hash"],

    classifiers=["Development Status :: 4 - Beta",
                 "License :: OSI Approved :: GNU General Public License v3 (GPLv3)",
                 "Operating System :: OS Independent",
                 "Environment :: Console",
                 "Topic :: System :: Filesystems",
                 "Topic :: System :: Monitoring",
                 "Topic :: System :: Archiving",
                 "Topic :: System :: Archiving :: Backup",
                 "Topic :: System :: Archiving :: Mirroring",
                 "Programming Language :: Python :: 3",
                 "Programming Language :: Python :: 3 :: Only",
                 "Programming Language :: Python :: 3.7",
                 "Programming Language :: Python :: 3.8",
                 "Programming Language :: Python :: 3.9",
                 "Programming Language :: Python :: 3.10",
                 "Programming Language :: Python :: 3.11",
                 "Programming Language :: Python :: 3.12",
                 ]
)
