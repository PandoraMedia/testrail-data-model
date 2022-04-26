"""
Reference: https://www.gurock.com/testrail/docs/api/reference/case-fields/

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

from enum import Enum
from dataclasses import dataclass, field
from typing import Optional, Dict


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
    def from_data(cls, data: Dict) -> TestRailCaseField:
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
            type_id=cls.TestRailCaseFieldType(data["type_id"]),
            configs=data["configs"],
            description=data["description"]
        )

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
