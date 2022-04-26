"""
Reference: https://www.gurock.com/testrail/docs/api/reference/projects/

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
from datetime import datetime
from enum import Enum
from typing import Dict, Optional, TYPE_CHECKING

if TYPE_CHECKING:  # pragma: no cover
    from .suite import TestRailSuite


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
    suites: Dict[int, TestRailSuite] = field(default_factory=dict, repr=False)

    @classmethod
    def from_data(cls, data: Dict) -> TestRailProject:
        """
        Convert a TestRail API response into a TestRailProject instance

        :param data: data from TestRail API response
        :type data: Dict
        :rtype: TestRailProject
        """
        completed_on = data["completed_on"]
        completed_on_dt = datetime.fromtimestamp(completed_on) if completed_on is not None else None
        return cls(
            project_id=data["id"],
            name=data["name"],
            url=data["url"],
            is_completed=data["is_completed"],
            suite_mode=cls.TestRailSuiteMode(data["suite_mode"]),
            show_announcement=data["show_announcement"],
            announcement=data["announcement"],
            completed_on=completed_on_dt
        )

    class TestRailSuiteMode(Enum):
        """
        Enumerated representation of a TestRailProject's "suite_mode" field
        """
        SINGLE_SUITE = 1
        SINGLE_SUITE_WITH_BASELINES = 2
        MULTIPLE_SUITES = 3
