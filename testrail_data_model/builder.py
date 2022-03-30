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

from typing import List, Generator, Optional, Dict

from testrail_api import TestRailAPI

from .model import (
    TestRailProject,
    TestRailSuite,
    TestRailSection,
    TestRailCase,
    TestRailCaseField,
    TestRailCaseType
)
from .stats import TestRailAPIRequestStats


class TestRailAPIObjectBuilder:
    """
    A class for providing Python object representations of TestRail objects

    Use this class in conjunction with TestRailProjectHierarchy to create
    a TestRailProject linked to TestRailSuites, TestRailSections, and TestRailCases

    :param api_client: client API for interacting with TestRail
    :type api_client: TestRailAPI
    :param stats: Used to track TestRail API metrics
    :type stats: Optional[TestRailAPIRequestStats]
    """

    def __init__(self, api_client: TestRailAPI, stats: Optional[TestRailAPIRequestStats] = None):
        """Constructor"""
        self._api_client = api_client
        self._stats = stats or TestRailAPIRequestStats()

    @property
    def api_client(self) -> TestRailAPI:
        """
        :return: Object for interacting with the TestRail API
        :rtype: TestRailAPI
        """
        return self._api_client

    @property
    def stats(self) -> TestRailAPIRequestStats:
        """
        :return: Object tracking TestRail API request metrics
        :rtype: TestRailAPIRequestStats
        """
        return self._stats

    def get_project(self, project_id: int) -> TestRailProject:
        """
        Reference: https://www.gurock.com/testrail/docs/api/reference/projects/#getproject

        :param project_id: the ID of the project data to retrieve
        :type project_id: int
        :rtype: TestRailProject
        """
        self.stats.get_project += 1
        response: Dict = self.api_client.projects.get_project(project_id=project_id)
        result = TestRailProject.from_data(response)
        return result

    def get_projects(self, is_completed: Optional[bool] = None, limit: int = 250, offset: int = 0)\
            -> Generator[TestRailProject, None, None]:
        """
        Reference: https://www.gurock.com/testrail/docs/api/reference/projects/#getprojects

        :param is_completed: True filters only completed, False for not-completed, None for no filtering
        :type is_completed: bool, optional (default: None)
        :param limit: return up to this many projects, default 250
        :type limit: int
        :param offset: skip this many projects before returning up to 'limit' projects, default 0
        :type offset: int
        :return: yields TestRailProject instances
        :rtype: Generator[TestRailProject, None, None]
        """
        kwargs = {} if is_completed is None else {'is_completed': int(is_completed)}
        while True:
            self.stats.get_projects += 1
            response = self.api_client.projects.get_projects(limit=limit, offset=offset, **kwargs)
            for item in response:
                yield TestRailProject.from_data(item)
            offset += len(response)
            if len(response) < limit:
                break

    def get_suite(self, suite_id: int) -> TestRailSuite:
        """
        Reference: https://www.gurock.com/testrail/docs/api/reference/suites/#getsuite

        :param suite_id: the ID of the suite data to retrieve
        :type suite_id: int
        :rtype: TestRailSuite
        """
        self.stats.get_suite += 1
        response: Dict = self.api_client.suites.get_suite(suite_id=suite_id)
        return TestRailSuite.from_data(response)

    def get_suites(self, project_id: int) -> List[TestRailSuite]:
        """
        Reference: https://www.gurock.com/testrail/docs/api/reference/suites/#getsuites

        :param project_id: the ID of the project from which to retrieve suite data
        :type project_id: int
        :rtype: List[TestRailSuite]
        """
        self.stats.get_suites += 1
        response: List[Dict] = self.api_client.suites.get_suites(project_id=project_id)
        return [TestRailSuite.from_data(item) for item in response]

    def get_section(self, section_id: int) -> TestRailSection:
        """
        Reference: https://www.gurock.com/testrail/docs/api/reference/sections/#getsection

        :param section_id: the ID of the section data to retrieve
        :type section_id: int
        :rtype: TestRailSection
        """
        self.stats.get_section += 1
        response: Dict = self.api_client.sections.get_section(section_id=section_id)
        return TestRailSection.from_data(response)

    def get_sections(self, project_id: int, suite_id: Optional[int] = None, limit: int = 250, offset: int = 0)\
            -> Generator[TestRailSection, None, None]:
        """
        Reference: https://www.gurock.com/testrail/docs/api/reference/sections/#getsections

        NOTE: This is a generator function which will retrieve section data
        from the server in batches. If maximum limit is 250 and the suite
        has 300 sections, this method will make 2 API requests, but since
        it is a generator it will only issue the requests as needed,
        i.e. when a for-loop requests the next item, but the previous batch
        has been exhausted.

        :param project_id: ID of the project from which to retrieve section data
        :type project_id: int
        :param suite_id: ID of suite (required if MULTIPLE_SUITES), default None
        :type suite_id: Optional[int]
        :param limit: return up to this many sections, default 250
        :type limit: int
        :param offset: skip this many sections before returning up to 'limit' sections, default 0
        :type offset: int
        :rtype: Generator[TestRailSection, None, None]
        """
        kwargs = {} if suite_id is None else {'suite_id': suite_id}
        while True:
            self.stats.get_sections += 1
            response = self.api_client.sections.get_sections(project_id=project_id, limit=limit, offset=offset,
                                                              **kwargs)
            for item in response:
                yield TestRailSection.from_data(item)
            offset += len(response)
            if len(response) < limit:
                break

    def add_section(self, project_id: int, name: str, suite_id: Optional[int] = None, parent_id: Optional[int] = None,
                    description: Optional[str] = None) -> TestRailSection:
        """
        Reference: https://www.gurock.com/testrail/docs/api/reference/sections/#addsection

        :param project_id: ID of the project to which to add the new section
        :type project_id: int
        :param name: the name of the new section
        :type name: str
        :param suite_id: ID of the suite (required if MULTIPLE_SUITES), default None
        :type suite_id: Optional[int]
        :param parent_id: ID of the parent section to associate to the new section, default None
        :type parent_id: Optional[int]
        :param description: description of the new section, default None
        :type description: Optional[str]
        :return: A new TestRailSection instance
        :rtype: TestRailSection
        """
        self.stats.add_section += 1
        response: Dict = self.api_client.sections.add_section(project_id=project_id, name=name, suite_id=suite_id,
                                                               parent_id=parent_id, description=description)
        return TestRailSection.from_data(response)

    def get_case(self, case_id: int) -> TestRailCase:
        """
        Reference: https://www.gurock.com/testrail/docs/api/reference/cases/#getcase

        :param case_id: ID of the case whose data to retrieve
        :type case_id: int
        :rtype: TestRailCase
        """
        self.stats.get_case += 1
        response: Dict = self.api_client.cases.get_case(case_id=case_id)
        return TestRailCase.from_data(response)

    def add_case(self, section_id: int, title: str, **kwargs) -> TestRailCase:
        """
        Reference: https://www.gurock.com/testrail/docs/api/reference/cases/#addcase

        :param section_id: the section ID to which the new case will be associated
        :type section_id: int
        :param title: title to set for the new case
        :type title: str
        :param kwargs: the fields to pass into the add_case API call
        :type kwargs: Dict
        :rtype: TestRailCase
        """
        self.stats.add_case += 1
        response: Dict = self.api_client.cases.add_case(section_id=section_id, title=title, **kwargs)
        return TestRailCase.from_data(response)

    def update_case(self, case: TestRailCase, **kwargs):
        """
        Reference: https://www.gurock.com/testrail/docs/api/reference/cases/#updatecase

        :param case: the case instance to update
        :type case: TestRailCase
        :param kwargs: fields to pass into the update_case API call
        :type kwargs: Dict
        :return: an updated TestRailCase instance
        :rtype: TestRailCase
        """
        self.stats.update_case += 1
        response: Dict = self.api_client.cases.update_case(case_id=case.case_id, **kwargs)
        return TestRailCase.from_data(response)

    def get_cases(self, project_id: int, suite_id: Optional[int] = None, limit: int = 250, offset: int = 0, **kwargs)\
            -> Generator[TestRailCase, None, None]:
        """
        https://www.gurock.com/testrail/docs/api/reference/cases/#getcases

        NOTE: This is a generator function which will retrieve case data
        from the server in batches. If maximum limit is 250 and the suite
        has 900 cases, this method will make 4 API requests, but since
        it is a generator it will only issue the requests as needed,
        i.e. when a for-loop requests the next item, but the previous batch
        has been exhausted.

        :param project_id: ID of project
        :type project_id: int,
        :param suite_id: ID of suite (required if MULTIPLE_SUITES), default None
        :type suite_id: Optional[int]
        :param limit: return up to this many cases, default 250
        :type limit: int
        :param offset: skip this many cases before returning up to 'limit' cases, default 0
        :type offset: int
        :rtype: Generator[TestRailCase, None, None]
        """
        if suite_id is not None:
            kwargs.update({'suite_id': suite_id})
        while True:
            self.stats.get_cases += 1
            response = self.api_client.cases.get_cases(project_id=project_id, limit=limit, offset=offset, **kwargs)
            for item in response:
                yield TestRailCase.from_data(item)
            offset += len(response)
            if len(response) < limit:
                break

    def get_case_fields(self) -> List[TestRailCaseField]:
        """
        https://www.gurock.com/testrail/docs/api/reference/case-fields/#getcasefields

        :return: List[TestRailCaseField]
        """
        self.stats.get_case_fields += 1
        response: List[Dict] = self.api_client.case_fields.get_case_fields()
        return [TestRailCaseField.from_data(item) for item in response]

    def get_case_types(self) -> List[TestRailCaseType]:
        """
        :return: list of TestRailCaseType objects from the TestRail API
        :rtype: List[TestRailCaseType]
        """
        self.stats.get_case_types += 1
        response: List[Dict] = self.api_client.case_types.get_case_types()
        return [TestRailCaseType.from_data(item) for item in response]

    def build_suite(self, project_id: int, suite_id: int) -> TestRailSuite:
        """
        Given a project_id and suite_id, build and return a TestRailSuite with
        all associated TestRailSection and TestRailCase objects loaded and linked
        together.

        :return: TestRailSuite
        """
        suite: TestRailSuite = self.get_suite(suite_id=suite_id)
        sections = self.get_sections(project_id=project_id, suite_id=suite_id)
        cases = self.get_cases(project_id=project_id, suite_id=suite_id)
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

    def create_new_section_for_path(self, suite: TestRailSuite, path: str) -> TestRailSection:
        """
        :param suite: TestRailSuite, the suite in which to create the section
        :type suite: TestRailSuite
        :param path: The intended path for the new section
        :type path: str
        :return: TestRailSection linked to an appropriate parent TestRailSection
        :rtype: TestRailSection
        """
        split_paths = path.rsplit('/', maxsplit=1)
        name = split_paths[-1]
        parent_path = None if len(split_paths) == 1 else split_paths[0]
        parent = None if parent_path is None else suite.section_for_path(parent_path)
        parent_id = None if parent is None else parent.section_id
        new_section = self.add_section(
            project_id=suite.project_id,
            name=name,
            suite_id=suite.suite_id,
            parent_id=parent_id
        )
        new_section.link(suite=suite, parent=parent)
        return new_section
