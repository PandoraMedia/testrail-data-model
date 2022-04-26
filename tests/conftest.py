import logging
import pytest
from unittest.mock import MagicMock, call, patch

from mimesis.schema import Schema, Field
from mimesis.locales import Locale
from testrail_api import TestRailAPI


from testrail_data_model.stats import TestRailAPIRequestStats
from testrail_data_model.adapter import TestRailAPIAdapter
from testrail_data_model.builder import TestRailAPIObjectBuilder
from testrail_data_model.model import (
    TestRailProject,
    TestRailSuite,
    TestRailSection,
    TestRailCase,
    TestRailCaseField,
    TestRailCaseType,
)

FIELD = Field(Locale.EN)

# Prevent pytest from trying to collect these classes
for item in [
    TestRailAPI,
    TestRailAPIAdapter,
    TestRailAPIRequestStats,
    TestRailAPIObjectBuilder,
    TestRailProject,
    TestRailSuite,
    TestRailSection,
    TestRailCase,
    TestRailCaseField,
    TestRailCaseType,
]:
    item.__test__ = False

logger = logging.getLogger()
logger.setLevel(logging.DEBUG)


def get_project_response():
    schema = Schema(schema=lambda: {
        "id": FIELD("integer_number", start=1, end=1000),
        "announcement": FIELD("text"),
        "completed_on": FIELD("timestamp"),
        "default_role_id": FIELD("integer_number", start=1, end=1000),
        "default_role": FIELD("word"),
        "is_completed": True,
        "name": FIELD("title"),
        "show_announcement": True,
        "suite_mode": 1,
        "url": FIELD("url"),
    })
    return schema.create(iterations=1)[0]


def get_suite_response():
    schema = Schema(schema=lambda: {
        "id": FIELD("integer_number", start=1, end=1000),
        "description": FIELD("text"),
        "name": FIELD("word"),
        "project_id": FIELD("integer_number", start=1, end=1000),
        "url": FIELD("url"),
        "is_baseline": False,
        "is_completed": True,
        "is_master": True,
        "completed_on": FIELD("timestamp")
    })
    return schema.create(iterations=1)[0]


def get_section_response():
    schema = Schema(schema=lambda: {
        "depth": FIELD("integer_number", start=1, end=1000),
        "description": FIELD("text"),
        "display_order": FIELD("integer_number", start=1, end=1000),
        "id": FIELD("integer_number", start=1, end=1000),
        "name": FIELD("word"),
        "parent_id": FIELD("integer_number", start=1, end=1000),
        "suite_id": FIELD("integer_number", start=1, end=1000)
    })
    return schema.create(iterations=1)[0]


def get_case_response():
    schema = Schema(schema=lambda: {
        "id": FIELD("integer_number", start=1, end=1000),
        "title": FIELD("text"),
        "section_id": FIELD("integer_number", start=1, end=1000),
        "template_id": FIELD("integer_number", start=1, end=1000),
        "type_id": FIELD("integer_number", start=1, end=1000),
        "priority_id": FIELD("integer_number", start=1, end=1000),
        "milestone_id": FIELD("integer_number", start=1, end=1000),
        "refs": None,
        "created_by": FIELD("integer_number", start=1, end=1000),
        "created_on": FIELD("timestamp"),
        "updated_by": FIELD("integer_number", start=1, end=1000),
        "updated_on": FIELD("timestamp"),
        "estimate": None,
        "estimate_forecast": None,
        "suite_id": FIELD("integer_number", start=1, end=1000),
        "display_order": FIELD("integer_number", start=1, end=1000),
        "is_deleted": int(bool(FIELD("integer_number", start=0, end=1))),
        "custom_automation_type": 0,
        "custom_preconds": FIELD("text"),
        "custom_steps": None,
        "custom_expected": None,
        "custom_steps_separated": [{"content": FIELD("text"), "expected": "", "additional_info": "", "refs": ""}],
        "custom_mission": FIELD("text"),
        "custom_goals": FIELD("text")
    })
    return schema.create(iterations=1)[0]


def get_case_fields_response():
    prop_name = FIELD("word").lower()
    schema = Schema(schema=lambda: {
        "configs": [
            {
                "context": {
                    "is_global": True,
                    "project_ids": None
                },
                "id": FIELD("integer_number", start=1, end=1000),
                "options": {
                    "default_value": "",
                    "format": "markdown",
                    "is_required": False,
                    "rows": FIELD("integer_number", start=1, end=1000)
                }
            }
        ],
        "description": FIELD("text"),
        "display_order": FIELD("integer_number", start=1, end=1000),
        "id": FIELD("increment"),
        "label": FIELD("word"),
        "name": prop_name,
        "system_name": f"custom_{prop_name}",
        "type_id": TestRailCaseField.TestRailCaseFieldType.TEXT.value
    })
    return schema.create(iterations=2)


def get_case_types_response():
    schema = Schema(schema=lambda: {
        "id": FIELD("increment"),
        "is_default": True,
        "name": FIELD("word")
    })
    return schema.create(iterations=2)


@pytest.fixture
def stats_fixture():
    stats = TestRailAPIRequestStats()
    stats.reset()
    return stats


@pytest.fixture
def mock_api_client():
    api = MagicMock(
        projects=MagicMock(
            get_project=MagicMock(
                return_value=get_project_response()
            ),
            get_projects=MagicMock(
                side_effect=[[get_project_response()], [get_project_response()], [get_project_response()], []]
            )
        ),
        suites=MagicMock(
            get_suite=MagicMock(
                return_value=get_suite_response()
            ),
            get_suites=MagicMock(
                return_value=[get_suite_response(), get_suite_response()]
            )
        ),
        sections=MagicMock(
            get_section=MagicMock(
                return_value=get_section_response()
            ),
            get_sections=MagicMock(
                side_effect=[[get_section_response()], [get_section_response()], [get_section_response()], []]
            ),
            add_section=MagicMock(
                return_value=get_section_response()
            )
        ),
        cases=MagicMock(
            get_case=MagicMock(
                return_value=get_case_response()
            ),
            get_cases=MagicMock(
                side_effect=[[get_case_response(), get_case_response()], [get_case_response()]]  # Trying limit=2
            ),
            add_case=MagicMock(
                return_value=get_case_response()
            ),
            update_case=MagicMock(
                return_value=get_case_response()
            ),
        ),
        case_fields=MagicMock(
            get_case_fields=MagicMock(
                return_value=get_case_fields_response()
            )
        ),
        case_types=MagicMock(
            get_case_types=MagicMock(
                return_value=get_case_types_response()
            )
        )
    )
    return api


@pytest.fixture
def suite_fixture():
    suite = TestRailSuite.from_data(get_suite_response())
    section1 = TestRailSection.from_data(get_section_response())
    section2 = TestRailSection.from_data(get_section_response())
    case1 = TestRailCase.from_data(get_case_response())
    case2 = TestRailCase.from_data(get_case_response())
    section2.suite_id = suite.suite_id
    section2.parent_id = section1.section_id
    section1.suite_id = suite.suite_id
    section1.parent_id = None
    case1.suite_id = suite.suite_id
    case1.section_id = section2.section_id
    case2.suite_id = suite.suite_id
    case2.section_id = section2.section_id
    case1.link(suite=suite, section=section2)
    case2.link(suite=suite, section=section2)
    section1.link(suite=suite, parent=None)
    section2.link(suite=suite, parent=section1)
    return suite
