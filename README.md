TestRail Data Model
===================

[![Python package][gh-action-python-package-badge]][gh-action-python-package]
[![PyPI][pypi-latest-release-badge]][pypi]
[![Downloads][pepy-downloads-badge]][pepy-downloads-link]
[![PyPI - Python Version][pypi-python-versions-badge]][pypi]
[![PyPI - Implementation][pypi-implementations-badge]][pypi]
[![License][license-badge]][license-link]
[![Coverage Status][coveralls-badge]][coveralls-link]

This package provides an object-oriented representation of TestRail data using
Python [data classes][python-dataclasses]. This object structure facilitates the development
of tools which programmatically interact with a TestRail service.

This wraps the [tolstislon/testrail-api][tolstislon-testrail-api] project, which in turn wraps the
[official TestRail API spec][gurock-testrail-api-documentation].

Example
-------

```python3
from testrail_api import TestRailAPI

from testrail_data_model.builder import TestRailAPIObjectBuilder
from testrail_data_model.adapter import TestRailAPIAdapter
from testrail_data_model.model import TestRailSection, TestRailCase, TestRailSuite

# From testrail-api client library
api_client = TestRailAPI(url="https://testrail-instance.com", email="email@email.org", password="password")

# Performs API requests and tracks stats
adapter = TestRailAPIAdapter(api_client=api_client)

# For building the TestRail dataclass object hierarchies (e.g. TestRailSuite)
builder = TestRailAPIObjectBuilder(adapter=adapter)

# Construct a TestRailSuite object linked to its associated TestRailSection and TestRailCase objects
suite: TestRailSuite = builder.build_suite(project_id=1, suite_id=1)

# Display the TestRailSuite object structure
for section_id, section in suite.sections.items():
   assert isinstance(section, TestRailSection)
   print("Section", section_id, section.path)
   for case_id, case in section.cases.items():
       assert isinstance(case, TestRailCase)
       print("Case", case_id, case.title)

# Show the number of API requests made
print(adapter.stats)
```

Authors
-------
* [Elliot Weiser](https://github.com/elliotweiser)
* [Rob Whitlock](https://github.com/robwhitlock666)
* [Rong Zheng](https://github.com/rzheng7)

[coveralls-badge]: https://coveralls.io/repos/github/PandoraMedia/testrail-data-model/badge.svg
[coveralls-link]: https://coveralls.io/github/PandoraMedia/testrail-data-model
[gh-action-python-package]: https://github.com/PandoraMedia/testrail-data-model/actions/workflows/python-package.yml
[gh-action-python-package-badge]: https://github.com/PandoraMedia/testrail-data-model/actions/workflows/python-package.yml/badge.svg
[gurock-testrail-api-documentation]: https://www.gurock.com/testrail/docs/api/
[license-badge]: https://img.shields.io/badge/License-Apache_2.0-blue.svg
[license-link]: https://raw.githubusercontent.com/PandoraMedia/testrail-data-model/master/LICENSE
[pepy-downloads-badge]: https://static.pepy.tech/personalized-badge/testrail-data-model?period=total&units=international_system&left_color=gray&right_color=blue&left_text=Downloads
[pepy-downloads-link]: https://pepy.tech/project/testrail-data-model
[pypi]: https://pypi.org/project/testrail-data-model/
[pypi-latest-release-badge]: https://img.shields.io/pypi/v/testrail-data-model?color=blue&label=pypi&logo=version
[pypi-implementations-badge]: https://img.shields.io/pypi/implementation/testrail-data-model
[pypi-python-versions-badge]: https://img.shields.io/pypi/pyversions/testrail-data-model.svg
[python-dataclasses]: https://docs.python.org/3/library/dataclasses.html
[tolstislon-testrail-api]: https://github.com/tolstislon/testrail-api