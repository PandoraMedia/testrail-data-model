"""
Reference: https://www.gurock.com/testrail/docs/api/reference/suites/

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

from dataclasses import dataclass, field
from typing import Dict, Optional, TYPE_CHECKING, Union
from datetime import datetime

if TYPE_CHECKING:  # pragma: no cover
    from .project import TestRailProject
    from .section import TestRailSection
    from .case import TestRailCase


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
    cases: Dict[int, TestRailCase] = field(default_factory=dict, repr=False)
    sections: Dict[int, TestRailSection] = field(default_factory=dict, repr=False)

    @classmethod
    def from_data(cls, data) -> TestRailSuite:
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
