"""
Reference: https://www.gurock.com/testrail/docs/api/reference/cases/

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

from __future__ import annotations

import time

from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional, Dict, TYPE_CHECKING

if TYPE_CHECKING:  # pragma: no cover
    from .suite import TestRailSuite
    from .section import TestRailSection


@dataclass
class TestRailCase:  # pylint: disable=too-many-instance-attributes
    """
    Dataclass for TestRail API "Cases"

    https://www.gurock.com/testrail/docs/api/reference/cases/
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
    def from_data(cls, data: Dict) -> TestRailCase:
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
