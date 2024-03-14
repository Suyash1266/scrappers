#!/usr/bin/python3
from setuptools import setup, find_packages

setup(
    name="scrappers",
    version="0.1.0",
    packages=find_packages(),
    install_requires=[
        "selenium>=4.18.1",
        "beautifulsoup4>=4.12.3",
    ],
    python_requires=">=3.10",
    package_dir={'scrappers': 'src'},
)