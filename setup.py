#!/usr/bin/env python
from setuptools import setup

NAME = "hyperspace"
setup(
    name=NAME,
    use_scm_version={
        "local_scheme": "dirty-tag",
        "write_to": f"{NAME}/_version.py",
        "fallback_version": "0.0.0",
    },
    author="Ross Fenning",
    author_email="github@rossfenning.co.uk",
    packages=[NAME],
    package_data={NAME: ["py.typed"]},
    description="General-purpose REST/hypermedia client.",
    setup_requires=[
        "setuptools_scm>=3.3.1",
        "pre-commit",
        "wheel",
    ],
    license="GPLv3+",
    classifiers=[
        "License :: OSI Approved :: GNU General Public License v3 or later (GPLv3+)",
        "Operating System :: OS Independent",
        "Programming Language :: Python",
        "Topic :: Software Development :: Libraries :: Python Modules",
    ],
    install_requires=[
        "requests",
        "rdflib",
        "rdflib-jsonld",
        "pyRdfa3",
        "beautifulsoup4",
        "html5lib",
        "uritemplate",
        "laconia",
    ],
    extras_require={
        "test": [
            "pytest",
            "pytest-pikachu",
            "pytest-mypy",
            "httpretty",
            "types-requests",
        ],
    },
)
