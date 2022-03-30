"""
Module which provides dataclass models for TestRail API objects

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

import time

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Optional, Dict, Union


class TestRailSuiteMode(Enum):
    """
    Enumerated representation of a TestRailProject's "suite_mode" field
    """
    SINGLE_SUITE = 1
    SINGLE_SUITE_WITH_BASELINES = 2
    MULTIPLE_SUITES = 3


@dataclass
class TestRailProject:
    """
    Dataclass for TestRail API "Projects"

    https://www.gurock.com/testrail/docs/api/reference/projects/
    """
    project_id: int
    name: str
    url: str
    is_completed: bool
    suite_mode: TestRailSuiteMode
    show_announcement: bool
    announcement: Optional[str] = None
    completed_on: Optional[datetime] = None
    suites: Dict[int, "TestRailSuite"] = field(default_factory=dict, repr=False)

    @classmethod
    def from_data(cls, data: Dict) -> "TestRailProject":
        """
        Convert a TestRail API response into a TestRailProject instance

        :param data: Dict, data from TestRail API response
        :return: TestRailProject
        """
        completed_on = data["completed_on"]
        completed_on_dt = datetime.fromtimestamp(completed_on) if completed_on is not None else None
        return cls(
            project_id=data["id"],
            name=data["name"],
            url=data["url"],
            is_completed=data["is_completed"],
            suite_mode=TestRailSuiteMode(data["suite_mode"]),
            show_announcement=data["show_announcement"],
            announcement=data["announcement"],
            completed_on=completed_on_dt
        )


@dataclass
class TestRailSuite:  # pylint: disable=too-many-instance-attributes
    """
    Dataclass for TestRail API "Suites"

    https://www.gurock.com/testrail/docs/api/reference/suites/
    """
    suite_id: int
    project_id: int
    name: str
    url: str
    is_completed: bool
    is_master: bool
    is_baseline: bool
    completed_on: Optional[datetime] = None
    description: Optional[str] = None
    project: Optional[TestRailProject] = field(default=None, repr=False)
    cases: Dict[int, "TestRailCase"] = field(default_factory=dict, repr=False)
    sections: Dict[int, "TestRailSection"] = field(default_factory=dict, repr=False)

    @classmethod
    def from_data(cls, data) -> "TestRailSuite":
        """
        Convert a TestRail API response into a TestRailSuite instance

        :param data: Dict, data from TestRail API response
        :return: TestRailSuite
        """
        return cls(
            suite_id=data["id"],
            project_id=data["project_id"],
            name=data["name"],
            description=data["description"],
            is_baseline=data["is_baseline"],
            is_completed=data["is_completed"],
            is_master=data["is_master"],
            url=data["url"]
        )

    @property
    def direct_sections(self) -> Dict[int, "TestRailSection"]:
        """
        :return: Dict[int, TestRailSection], dictionary of sections with no parent section
        """
        return {section_id: section for section_id, section in self.sections.items() if section.parent_id is None}

    @property
    def direct_cases(self) -> Dict[int, "TestRailCase"]:
        """
        :return: Dict[int, TestRailCase], dictionary of cases which do not belong to a section
        """
        return {case_id: case for case_id, case in self.cases.items() if case.section_id is None}

    @property
    def all_section_paths(self) -> Dict[int, str]:
        """
        :return: Dict[int, str], dictionary of section_ids to their matching full paths
        """
        return {section_id: section.path for section_id, section in self.sections.items()}

    def section_for_path(self, path: str) -> Union["TestRailSection", None]:
        """
        Return the appropriate TestRailSection, if it exists, corresponding to a given path.
        If no TestRailSection is found, return None.

        :param path: str, the path which will be used to find a matching TestRailSection
        :return: Union[TestRailSection, None]
        """
        for section_id, full_section_path in self.all_section_paths.items():
            if path == full_section_path:
                return self.sections[section_id]
        return None


@dataclass
class TestRailSection:  # pylint: disable=too-many-instance-attributes
    """
    Dataclass for TestRail API "Sections"

    https://www.gurock.com/testrail/docs/api/reference/sections/
    """
    section_id: int
    suite_id: int
    depth: int
    display_order: int
    name: str
    parent_id: Optional[int] = None
    description: Optional[str] = None
    suite: Optional[TestRailSuite] = field(default=None, repr=False)
    parent: Optional["TestRailSection"] = field(default=None, repr=False)
    sections: Dict[int, "TestRailSection"] = field(default_factory=dict, repr=False)
    cases: Dict[int, "TestRailCase"] = field(default_factory=dict, repr=False)

    @classmethod
    def from_data(cls, data) -> "TestRailSection":
        """
        Convert a TestRail API response into a TestRailSection instance

        :param data: Dict, data from TestRail API response
        :return: TestRailSection
        """
        return cls(
            section_id=data["id"],
            suite_id=data["suite_id"],
            depth=data["depth"],
            display_order=data["display_order"],
            name=data["name"],
            parent_id=data["parent_id"],
            description=data.get("description", None)
        )

    @property
    def path(self) -> str:
        """
        :return: str, full path of the section
        """
        section_names = []
        section: TestRailSection = self
        while section is not None:
            section_names.append(section.name)
            section = section.parent
        return "/".join(reversed(section_names))

    def move(self, new_parent: Optional["TestRailSection"] = None):
        """
        Move this TestRailSection instance to a new parent (can be None)

        :param new_parent: New parent TestRailSection (default: None)
        :type new_parent: Optional[TestRailSection]
        """
        suite = self.suite
        self.unlink()
        self.parent_id = new_parent.section_id if new_parent is not None else None
        self.link(suite=suite, parent=new_parent)

    def unlink(self):
        """
        Unlink this TestRailSection from other dataclasses
        """
        while len(self.sections) > 0:
            _, inner_section = self.sections.popitem()
            inner_section.unlink()
        while len(self.cases) > 0:
            _, inner_case = self.cases.popitem()
            inner_case.unlink()
        if self.suite is not None and self.section_id in self.suite.sections:
            del self.suite.sections[self.section_id]
            self.suite = None
        if self.parent is not None and self.section_id in self.parent.sections:
            del self.parent.sections[self.section_id]
            self.parent = None

    def link(self, suite: TestRailSuite, parent: Optional["TestRailSection"] = None):
        """
        Link this TestRailSection to a TestRailSuite and an optional parent TestRailSection

        :param suite: TestRailSuite, the test-suite
        :param parent: Optional[TestRailSection], the parent TestRailSection
        """
        # Suite -> Section
        if self.suite_id != suite.suite_id:
            raise ValueError(f"section.suite_id ({self.suite_id}) does not match"
                             f" suite.suite_id ({suite.suite_id})")
        suite.sections[self.section_id] = self

        # Section -> Suite
        self.suite = suite
        # Section (Child) -> Section (Parent)
        self.parent = parent

        if parent is not None:
            if parent.section_id != self.parent_id:
                raise ValueError(f"section.parent_id ({self.parent_id}) does not match"
                                 f" parent.section_id ({parent.section_id})")

            # Section (Parent) -> Section (Child)
            parent.sections[self.section_id] = self


@dataclass
class TestRailCase:  # pylint: disable=too-many-instance-attributes
    """
    Dataclass for TestRail API "Cases"

    Reference: https://www.gurock.com/testrail/docs/api/reference/cases/
    """
    case_id: int
    suite_id: int
    created_by: int
    created_on: datetime
    priority_id: int
    template_id: int
    title: str
    type_id: int
    updated_by: int
    updated_on: datetime
    is_deleted: bool
    custom_fields: Dict
    display_order: Optional[int] = None
    estimate: Optional[str] = None
    estimate_forecast: Optional[str] = None
    section_id: Optional[int] = None
    milestone_id: Optional[int] = None
    refs: Optional[str] = None
    section: Optional[TestRailSection] = field(default=None, repr=False, init=False)
    suite: Optional[TestRailSuite] = field(default=None, repr=False, init=False)

    def __getattr__(self, attr: str):
        """
        Return the "custom" attribute of the given TestRailCase instance.
        TestRail prefixes custom case fields with "custom_", so this method
        allows access to these attributes. If field "custom_uuid" exists on a
        test case in TestRail, then it is possible to access the value of this field
        by executing "case.uuid".

        :param attr: the attribute name
        :type attr: str
        :raises: AttributeError if "custom_" attr does not exist
        :raises: ValueError if attr is empty string
        :return: the value of the attribute
        """
        if len(attr) == 0:
            raise ValueError("Attribute must be non-zero length")
        attr_name = f"custom_{attr}"
        if attr_name not in self.custom_fields:
            raise AttributeError(f"{type(self).__name__} instance has no custom field: '{attr_name}'")
        return self.custom_fields[attr_name]

    def unlink(self):
        """
        Unlink this TestRailCase from other dataclasses
        """
        if self.suite is not None and self.case_id in self.suite.cases:
            del self.suite.cases[self.case_id]
            self.suite = None
        if self.section is not None and self.case_id in self.section.cases:
            del self.section.cases[self.case_id]
            self.section = None

    def link(self, suite: TestRailSuite, section: Optional[TestRailSection] = None):
        """
        Link this TestRailCase to a TestRailSuite and an optional TestRailSection

        :param suite: the TestRailSuite instance to which the case will be linked
        :type suite: TestRailSuite
        :param section: the parent TestRailSection, optional
        :type section: Optional[TestRailSection]
        """
        # Suite -> Case
        if self.suite_id != suite.suite_id:
            raise ValueError(f"case.suite_id ({self.suite_id}) does not match "
                             f"suite.suite_id ({suite.suite_id})")
        suite.cases[self.case_id] = self

        # Case -> Suite
        self.suite = suite
        # Case -> Section
        self.section = section
        if section is not None:
            if section.section_id != self.section_id:
                raise ValueError(f"case.section_id ({self.section_id}) does not match "
                                 f"section.section_id ({section.section_id})")

            # Section -> Case
            section.cases[self.case_id] = self

    @classmethod
    def from_data(cls, data: Dict) -> "TestRailCase":
        """
        Convert a TestRail API response into a TestRailCase instance

        :param data: data from TestRail API response
        :type data: Dict
        :rtype: TestRailCase
        """
        custom_fields = {}
        for key, value in data.items():
            if key.startswith("custom_"):
                custom_fields[key] = value
        return cls(
            case_id=data["id"],
            suite_id=data["suite_id"],
            created_by=data["created_by"],
            created_on=datetime.fromtimestamp(data["created_on"]),
            priority_id=data["priority_id"],
            template_id=data["template_id"],
            title=data["title"],
            type_id=data["type_id"],
            updated_by=data["updated_by"],
            updated_on=datetime.fromtimestamp(data["updated_on"]),
            is_deleted=bool(data.get("is_deleted", 0)),
            display_order=data.get("display_order", None),
            custom_fields=custom_fields,
            estimate=data["estimate"],
            estimate_forecast=data["estimate_forecast"],
            section_id=data["section_id"],
            milestone_id=data["milestone_id"],
            refs=data["refs"]
        )

    def to_dict(self) -> Dict[str, object]:
        """
        :return: a dictionary representation of this instance
        :rtype: Dict[str, object]
        """
        result = {
            'id': self.case_id,
            'suite_id': self.suite_id,
            'created_by': self.created_by,
            'created_on': int(time.mktime(self.created_on.timetuple())),
            'priority_id': self.priority_id,
            'template_id': self.template_id,
            'title': self.title,
            'type_id': self.type_id,
            'updated_by': self.updated_by,
            'updated_on': int(time.mktime(self.updated_on.timetuple())),
            'is_deleted': int(self.is_deleted),
            'display_order': self.display_order,
            'estimate': self.estimate,
            'estimate_forecast': self.estimate_forecast,
            'section_id': self.section_id,
            'milestone_id': self.milestone_id,
            'refs': self.refs
        }
        result.update(self.custom_fields)
        return result

    @property
    def path(self) -> str:
        """
        :return: the full section path of this TestRailCase
        :rtype: str
        """
        return self.section.path if self.section is not None else None


class TestRailCaseFieldType(Enum):
    """
    Reference: https://www.gurock.com/testrail/docs/api/reference/case-fields/
    """
    STRING = 1
    INTEGER = 2
    TEXT = 3
    URL = 4
    CHECKBOX = 5
    DROPDOWN = 6
    USER = 7
    DATE = 8
    MILESTONE = 9
    STEPS = 10
    # There is no 11
    MULTI_SELECT = 12


@dataclass
class TestRailCaseField:
    """
    Dataclass for TestRail API "Case Fields"

    Reference: https://www.gurock.com/testrail/docs/api/reference/case-fields/
    """
    case_field_id: int
    display_order: int
    label: str
    name: str
    system_name: str
    type_id: TestRailCaseFieldType
    configs: Dict = field(default_factory=dict)
    description: Optional[str] = None

    @classmethod
    def from_data(cls, data: Dict) -> "TestRailCaseField":
        """
        :param data: response data from TestRail API
        :type data: Dict
        :rtype: TestRailCaseField
        """
        return cls(
            case_field_id=data["id"],
            display_order=data["display_order"],
            label=data["label"],
            name=data["name"],
            system_name=data["system_name"],
            type_id=TestRailCaseFieldType(data["type_id"]),
            configs=data["configs"],
            description=data["description"]
        )


@dataclass
class TestRailCaseType:
    """
    Dataclass for TestRail API "Case Types"

    Reference: https://www.gurock.com/testrail/docs/api/reference/case-types/
    """
    case_type_id: int
    is_default: bool
    name: str

    @classmethod
    def from_data(cls, data: Dict) -> "TestRailCaseType":
        """
        :param data: response data from TestRail API
        :type data: Data
        :rtype: TestRailCaseType
        """
        return cls(
            case_type_id=data["id"],
            is_default=data["is_default"],
            name=data["name"]
        )
