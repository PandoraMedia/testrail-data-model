"""
Reference: https://www.gurock.com/testrail/docs/api/reference/case-types/

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

from dataclasses import dataclass
from typing import Dict


@dataclass
class TestRailCaseType:
    """
    Dataclass for TestRail API "Case Types"

    https://www.gurock.com/testrail/docs/api/reference/case-types/
    """
    case_type_id: int
    is_default: bool
    name: str

    @classmethod
    def from_data(cls, data: Dict) -> TestRailCaseType:
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
