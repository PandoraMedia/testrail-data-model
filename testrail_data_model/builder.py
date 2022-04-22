"""
Module providing a builder class for creating TestRailAPI model dataclass instances

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

from .adapter import TestRailAPIAdapter
from .model import TestRailSuite


class TestRailAPIObjectBuilder:  # pylint: disable=too-few-public-methods
    """
    A builder class for linked TestRail object hierarchies, e.g. TestRailSuite

    :param adapter: object wrapping TestRailAPI and tracking request stats
    :type adapter: TestRailAPIAdapter
    """

    def __init__(self, adapter: TestRailAPIAdapter):
        """Constructor"""
        self._adapter = adapter

    def build_suite(self, project_id: int, suite_id: int) -> TestRailSuite:
        """
        Given a project_id and suite_id, build and return a TestRailSuite with
        all associated TestRailSection and TestRailCase objects loaded and linked
        together.

        :param project_id: TestRail Project ID
        :type project_id: int
        :param suite_id: TestRail Suite ID
        :type suite_id: int
        :return: A TestRailSuite object linked to associated TestRailSection and TestRailCase objects
        :rtype: TestRailSuite
        """
        suite: TestRailSuite = self._adapter.get_suite(suite_id=suite_id)
        sections = self._adapter.get_sections(project_id=project_id, suite_id=suite_id)
        cases = self._adapter.get_cases(project_id=project_id, suite_id=suite_id)
        section_dict = {section.section_id: section for section in sections}
        case_dict = {case.case_id: case for case in cases}

        # Suite -> Sections
        suite.sections.update(section_dict)
        # Suite -> Cases
        suite.cases.update(case_dict)

        for _, section in section_dict.items():
            parent = section_dict.get(section.parent_id, None)
            section.link(suite=suite, parent=parent)

        for _, case in case_dict.items():
            section = section_dict.get(case.section_id, None)
            case.link(suite=suite, section=section)
        return suite
