"""
Reference: https://www.gurock.com/testrail/docs/api/reference/sections/

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
from typing import Dict, Optional, TYPE_CHECKING

if TYPE_CHECKING:  # pragma: no cover
    from .suite import TestRailSuite
    from .case import TestRailCase


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
    parent: Optional[TestRailSection] = field(default=None, repr=False)
    sections: Dict[int, TestRailSection] = field(default_factory=dict, repr=False)
    cases: Dict[int, TestRailCase] = field(default_factory=dict, repr=False)

    @classmethod
    def from_data(cls, data) -> TestRailSection:
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

    def move(self, new_parent: Optional[TestRailSection] = None):
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

    def link(self, suite: TestRailSuite, parent: Optional[TestRailSection] = None):
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
