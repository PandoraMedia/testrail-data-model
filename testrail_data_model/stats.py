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

from dataclasses import dataclass, asdict
from .singleton import Singleton


@dataclass
class TestRailAPIRequestStats(metaclass=Singleton):  # pylint: disable=too-many-instance-attributes
    """
    Class for counting API requests
    """
    # projects
    get_project: int = 0
    get_projects: int = 0

    # suites
    get_suite: int = 0
    get_suites: int = 0

    # sections
    get_section: int = 0
    get_sections: int = 0
    add_section: int = 0
    move_section: int = 0
    delete_section: int = 0

    # cases
    get_case: int = 0
    get_cases: int = 0
    add_case: int = 0
    update_case: int = 0
    update_cases: int = 0
    delete_case: int = 0
    delete_cases: int = 0

    # case fields
    get_case_fields: int = 0

    # case types
    get_case_types: int = 0

    @property
    def total(self) -> int:
        """
        :return: int, the total count of all API requests
        """
        return sum([
            self.get_project,
            self.get_projects,
            self.get_suite,
            self.get_suites,
            self.get_section,
            self.get_sections,
            self.add_section,
            self.move_section,
            self.delete_section,
            self.get_case,
            self.get_cases,
            self.add_case,
            self.update_case,
            self.update_cases,
            self.delete_case,
            self.get_case_fields,
            self.get_case_types
        ])

    def reset(self):
        """
        Reset the state of this singleton object. Probably not useful outside of testing.
        """
        self_as_dict = asdict(self)
        for key, _ in self_as_dict.items():
            setattr(self, key, 0)
