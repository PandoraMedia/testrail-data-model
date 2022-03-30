"""
Module to track stats about interactions with the TestRail API

Copyright 2022 SiriusXM-Pandora

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

    http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.
"""

from setuptools import setup, find_packages

from pathlib import Path

from pbr.packaging import (
    get_version,
    get_requirements_files,
    parse_requirements
)

readme = Path(".", "README.md").absolute()
with readme.open("r", encoding="utf-8") as file:
    long_description = file.read()

package_name = 'testrail-data-model'
pkgs = find_packages(exclude=["tests"])
version = get_version(package_name=package_name)

setup(
    name=package_name,
    author="Elliot Weiser",
    author_email="elliot.weiser@gmail.com",
    packages=pkgs,
    version=version,
    install_requires=parse_requirements(get_requirements_files()),
    description="Package for creating and managing objects from the TestRail API",
    python_requires=">=3.8",
    classifiers=[
        "Intended Audience :: Developers",
        "Natural Language :: English",
        "Operating System :: OS Independent",
        "Programming Language :: Python",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: Implementation :: CPython",
        "Programming Language :: Python :: Implementation :: PyPy",
        "Topic :: Software Development :: Libraries :: Python Modules",
    ],
    platforms=["any"],
    keywords=[
        "testrail",
        "testrail-api",
        "api",
        "testrail-client",
        "client",
        "testrail-objects",
        "objects"
    ],
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/PandoraMedia/testrail-data-model"

)