TestRail Data Model
===================

[![Python package][gh-action-python-package-badge]][gh-action-python-package]
[![License][license-badge]][license-link]

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
from testrail_data_model.model import TestRailSection, TestRailCase

# From testrail-api client library
api = TestRailAPI(url="https://testrail-instance.com", email="email@email.org", password="password")

# For building the TestRail dataclass object instances
builder = TestRailAPIObjectBuilder(api_client=api)

# Construct a TestRailSuite object linked to its associated TestRailSection and TestRailCase objects
suite = builder.build_suite(project_id=1, suite_id=1)

# Display the TestRailSuite object structure
for section_id, section in suite.sections.items():
   assert isinstance(section, TestRailSection)
   print("Section", section_id, section.path)
   for case_id, case in section.cases.items():
       assert isinstance(case, TestRailCase)
       print("Case", case_id, case.title)

# Show the number of API requests made
print(builder.stats)
```

Authors
-------
* [Elliot Weiser](https://github.com/elliotweiser)
* [Rob Whitlock](https://github.com/robwhitlock666)
* [Rong Zheng](https://github.com/rzheng7)

[python-dataclasses]: https://docs.python.org/3/library/dataclasses.html
[gurock-testrail-api-documentation]: https://www.gurock.com/testrail/docs/api/
[tolstislon-testrail-api]: https://github.com/tolstislon/testrail-api
[gh-action-python-package]: https://github.com/PandoraMedia/testrail-data-model/actions/workflows/python-package.yml
[gh-action-python-package-badge]: https://github.com/PandoraMedia/testrail-data-model/actions/workflows/python-package.yml/badge.svg
[license-badge]: https://img.shields.io/badge/License-Apache_2.0-blue.svg
[license-link]: https://raw.githubusercontent.com/PandoraMedia/testrail-data-model/master/LICENSE
