from typing import Generator
from unittest.mock import call, patch

from testrail_api import TestRailAPI

from testrail_data_model.builder import TestRailAPIObjectBuilder
from testrail_data_model.model import (
    TestRailProject,
    TestRailSuite,
    TestRailSection,
    TestRailCase,
    TestRailCaseField,
    TestRailCaseType
)

from .conftest import *

# Prevent pytest from discovering these classes
for item in [
    TestRailAPI,
    TestRailAPIObjectBuilder,
    TestRailAPIRequestStats,
    TestRailProject,
    TestRailSuite,
    TestRailSection,
    TestRailCase,
    TestRailCaseField,
    TestRailCaseFieldType,
    TestRailCaseType
]:
    item.__test__ = False


def test_get_project_returns_correct_instance_type(mock_api_client, stats_fixture):
    project_id = FIELD("integer_number", start=1, end=1000)
    subject = TestRailAPIObjectBuilder(api_client=mock_api_client, stats=stats_fixture)
    actual = subject.get_project(project_id=project_id)
    mock_api_client.projects.get_project.assert_called_once_with(project_id=project_id)
    assert isinstance(actual, TestRailProject)
    assert actual.announcement is not None
    assert subject.stats.get_project == 1
    assert subject.stats.total == 1


def test_get_projects_returns_generator_of_project_instances(mock_api_client, stats_fixture):
    subject = TestRailAPIObjectBuilder(api_client=mock_api_client, stats=stats_fixture)
    actual = subject.get_projects(limit=1)
    assert isinstance(actual, Generator)
    for project in actual:
        assert isinstance(project, TestRailProject)
        assert project.announcement is not None
    expected_calls = [call(limit=1, offset=i) for i in range(4)]
    mock_api_client.projects.get_projects.assert_has_calls(calls=expected_calls, any_order=False)
    assert subject.stats.get_projects == 4
    assert subject.stats.total == 4


def test_get_suite_returns_correct_instance_type(mock_api_client, stats_fixture):
    subject = TestRailAPIObjectBuilder(api_client=mock_api_client, stats=stats_fixture)
    suite_id = FIELD("integer_number", start=1, end=1000)
    actual = subject.get_suite(suite_id=suite_id)
    mock_api_client.suites.get_suite.assert_called_once_with(suite_id=suite_id)
    assert isinstance(actual, TestRailSuite)
    assert actual.description is not None
    assert subject.stats.get_suite == 1
    assert subject.stats.total == 1


def test_get_suites_returns_list_of_suite_instances(mock_api_client, stats_fixture):
    subject = TestRailAPIObjectBuilder(api_client=mock_api_client, stats=stats_fixture)
    project_id = FIELD("integer_number", start=1, end=1000)
    actual = subject.get_suites(project_id=project_id)
    assert len(actual) > 0
    for suite in actual:
        assert isinstance(suite, TestRailSuite)
        assert suite.description is not None
    mock_api_client.suites.get_suites.assert_called_once_with(project_id=project_id)
    assert subject.stats.get_suites == 1
    assert subject.stats.total == 1


def test_get_sections_returns_correct_instance_type(mock_api_client, stats_fixture):
    subject = TestRailAPIObjectBuilder(api_client=mock_api_client, stats=stats_fixture)
    section_id = FIELD("integer_number", start=1, end=1000)
    actual = subject.get_section(section_id=section_id)
    mock_api_client.sections.get_section.assert_called_once_with(section_id=section_id)
    assert isinstance(actual, TestRailSection)
    assert actual.description is not None
    assert subject.stats.get_section == 1
    assert subject.stats.total == 1


def test_get_section_returns_generator_of_sections(mock_api_client, stats_fixture):
    subject = TestRailAPIObjectBuilder(api_client=mock_api_client, stats=stats_fixture)
    project_id = FIELD("integer_number", start=1, end=1000)
    suite_id = FIELD("integer_number", start=1, end=1000)
    actual = subject.get_sections(project_id=project_id, suite_id=suite_id, limit=1, offset=0)
    for section in actual:
        assert isinstance(section, TestRailSection)
        assert section.description is not None
    expected_calls = [call(limit=1, offset=i, project_id=project_id, suite_id=suite_id) for i in range(4)]
    mock_api_client.sections.get_sections.assert_has_calls(calls=expected_calls, any_order=False)
    assert subject.stats.total == 4
    assert subject.stats.get_sections == 4


def test_add_section_returns_correct_instance_type(mock_api_client, stats_fixture):
    subject = TestRailAPIObjectBuilder(api_client=mock_api_client, stats=stats_fixture)
    project_id = FIELD("integer_number", start=1, end=1000)
    suite_id = FIELD("integer_number", start=1, end=1000)
    name = FIELD("word")
    description = FIELD("text")
    parent_id = FIELD("integer_number", start=1, end=1000)
    actual = subject.add_section(
        project_id=project_id,
        suite_id=suite_id,
        name=name,
        description=description,
        parent_id=parent_id
    )
    mock_api_client.sections.add_section.assert_called_once_with(
        project_id=project_id,
        suite_id=suite_id,
        name=name,
        description=description,
        parent_id=parent_id
    )
    assert isinstance(actual, TestRailSection)
    assert actual.description is not None
    assert subject.stats.add_section == 1
    assert subject.stats.total == 1


def test_get_case_returns_correct_instance_type(mock_api_client, stats_fixture):
    case_id = FIELD("integer_number", start=1, end=1000)
    subject = TestRailAPIObjectBuilder(api_client=mock_api_client, stats=stats_fixture)
    actual = subject.get_case(case_id=case_id)
    assert isinstance(actual, TestRailCase)
    assert len(actual.steps_separated) == 1
    assert actual.steps_separated[0]["content"] is not None
    assert subject.stats.get_case == 1
    assert subject.stats.total == 1
    mock_api_client.cases.get_case.assert_called_once_with(case_id=case_id)


def test_add_case_returns_correct_instance_type(mock_api_client, stats_fixture):
    section_id = FIELD("integer_number", start=1, end=1000)
    title = FIELD("title")
    subject = TestRailAPIObjectBuilder(api_client=mock_api_client, stats=stats_fixture)
    actual = subject.add_case(section_id=section_id, title=title)
    assert isinstance(actual, TestRailCase)
    assert len(actual.steps_separated) == 1
    assert actual.steps_separated[0]["content"] is not None
    assert subject.stats.add_case == 1
    assert subject.stats.total == 1
    mock_api_client.cases.add_case.assert_called_once_with(section_id=section_id, title=title)


def test_update_case_returns_correct_instance_type(mock_api_client, stats_fixture):
    case_id = FIELD("integer_number", start=1, end=1000)
    section_id = FIELD("integer_number", start=1, end=1000)
    title = FIELD("title")
    subject = TestRailAPIObjectBuilder(api_client=mock_api_client, stats=stats_fixture)
    start_case = subject.get_case(case_id=case_id)
    actual = subject.update_case(case=start_case, title=title, section_id=section_id)
    assert isinstance(actual, TestRailCase)
    assert len(actual.steps_separated) == 1
    assert actual.steps_separated[0]["content"] is not None
    assert subject.stats.update_case == 1
    assert subject.stats.total == 2
    mock_api_client.cases.update_case.assert_called_once_with(
        case_id=start_case.case_id,
        title=title,
        section_id=section_id
    )


def test_get_cases_returns_generator_of_cases(mock_api_client, stats_fixture):
    subject = TestRailAPIObjectBuilder(api_client=mock_api_client, stats=stats_fixture)
    project_id = FIELD("integer_number", start=1, end=1000)
    actual = subject.get_cases(project_id=project_id, limit=2, offset=0)
    assert isinstance(actual, Generator)
    for case in actual:
        assert isinstance(case, TestRailCase)
        assert len(case.steps_separated) == 1
        assert case.steps_separated[0]["content"] is not None
    expected_calls = [call(project_id=project_id, limit=2, offset=i) for i in range(0, 4, 2)]
    mock_api_client.cases.get_cases.assert_has_calls(expected_calls, any_order=False)
    assert subject.stats.get_cases == 2
    assert subject.stats.total == 2


def test_get_cases_with_suite_returns_generator_of_cases(mock_api_client, stats_fixture):
    subject = TestRailAPIObjectBuilder(api_client=mock_api_client, stats=stats_fixture)
    project_id = FIELD("integer_number", start=1, end=1000)
    suite_id = FIELD("integer_number", start=1, end=1000)
    actual = subject.get_cases(project_id=project_id, suite_id=suite_id, limit=2, offset=0)
    assert isinstance(actual, Generator)
    for case in actual:
        assert isinstance(case, TestRailCase)
        assert len(case.steps_separated) == 1
        assert case.steps_separated[0]["content"] is not None
    expected_calls = [call(project_id=project_id, suite_id=suite_id, limit=2, offset=i) for i in range(0, 4, 2)]
    mock_api_client.cases.get_cases.assert_has_calls(expected_calls, any_order=False)
    assert subject.stats.get_cases == 2
    assert subject.stats.total == 2


def test_get_case_fields_returns_correct_instance_type(mock_api_client, stats_fixture):
    subject = TestRailAPIObjectBuilder(api_client=mock_api_client, stats=stats_fixture)
    actual = subject.get_case_fields()
    assert len(actual) > 0
    for field_item in actual:
        assert isinstance(field_item, TestRailCaseField)
        assert field_item.description is not None
    assert subject.stats.get_case_fields == 1
    assert subject.stats.total == 1


def test_create_new_section_for_path(mock_api_client, stats_fixture):
    subject = TestRailAPIObjectBuilder(api_client=mock_api_client, stats=stats_fixture)
    suite = TestRailSuite.from_data(get_suite_response())
    new_section = TestRailSection.from_data(get_section_response())
    parent_section = TestRailSection.from_data(get_section_response())

    # Set up ID (foreign key) links without explicitly linking objects
    new_section.suite_id = suite.suite_id
    parent_section.suite_id = suite.suite_id
    new_section.parent_id = parent_section.section_id

    with patch.object(suite, 'section_for_path', return_value=parent_section) as section_for_path_mock:
        with patch.object(subject, 'add_section', return_value=new_section) as add_section_patch:
            actual = subject.create_new_section_for_path(suite=suite, path='path/to/new/section')
    assert isinstance(actual, TestRailSection)
    assert actual is new_section
    assert actual.suite is suite
    assert actual.parent is not None
    assert actual.parent is parent_section
    add_section_patch.assert_called_once_with(
        name="section",
        project_id=suite.project_id,
        suite_id=suite.suite_id,
        parent_id=parent_section.section_id
    )
    section_for_path_mock.assert_called_once_with('path/to/new')


def test_build_suite_returns_suite_instance_with_links(mock_api_client, stats_fixture):
    subject = TestRailAPIObjectBuilder(api_client=mock_api_client, stats=stats_fixture)
    suite = TestRailSuite.from_data(get_suite_response())
    top_section = TestRailSection.from_data(get_section_response())
    bottom_section = TestRailSection.from_data(get_section_response())
    case = TestRailCase.from_data(get_case_response())

    project_id = suite.project_id
    suite_id = suite.suite_id

    # Set up ID (foreign key) matching without explicitly linking
    top_section.suite_id = suite_id
    top_section.parent_id = None
    bottom_section.suite_id = suite_id
    case.suite_id = suite_id
    case.section_id = bottom_section.section_id
    bottom_section.parent_id = top_section.section_id

    with patch.object(subject, 'get_cases', return_value=[case]):
        with patch.object(subject, 'get_sections', return_value=[top_section, bottom_section]):
            with patch.object(subject, 'get_suite', return_value=suite):
                actual = subject.build_suite(project_id=project_id, suite_id=suite_id)
    assert isinstance(actual, TestRailSuite)
    assert actual is suite

    # Check the linking of the objects
    assert len(suite.sections) == 2
    assert len(suite.cases) == 1
    assert list(suite.direct_sections.values()) == [top_section]
    assert list(suite.direct_cases.values()) == []
    assert suite.cases[case.case_id] is case
    assert suite.all_section_paths == {
        top_section.section_id: top_section.path,
        bottom_section.section_id: bottom_section.path
    }
    assert suite.section_for_path(top_section.path) is top_section
    assert suite.section_for_path(bottom_section.path) is bottom_section
    assert suite.section_for_path(bottom_section.path + "foobar") is None

    assert top_section.suite is suite
    assert top_section.parent is None
    assert len(top_section.cases) == 0

    assert bottom_section.suite is suite
    assert bottom_section.parent is top_section
    assert len(bottom_section.cases) == 1
    assert bottom_section.cases[case.case_id] is case
    assert bottom_section.path == f"{top_section.name}/{bottom_section.name}"

    assert case.case_id in suite.cases
    assert case.suite is suite
    assert case.section is bottom_section
    assert case.path == f"{top_section.name}/{bottom_section.name}"

    # Try unlinking
    case.unlink()
    top_section.unlink()

    assert len(suite.cases) == 0
    assert len(suite.sections) == 0
    assert len(top_section.sections) == 0
    assert len(bottom_section.cases) == 0


def test_section_suite_linking_fails_if_ids_unequal():
    suite = TestRailSuite.from_data(get_suite_response())
    section = TestRailSection.from_data(get_section_response())
    section.suite_id = suite.suite_id + 1
    with pytest.raises(ValueError) as exc_info:
        section.link(suite=suite)
    assert str(exc_info.value) == \
           f"section.suite_id ({section.suite_id}) does not match suite.suite_id ({suite.suite_id})"


def test_section_parent_linking_fails_if_ids_unequal():
    suite = TestRailSuite.from_data(get_suite_response())
    section = TestRailSection.from_data(get_section_response())
    parent = TestRailSection.from_data(get_section_response())
    section.suite_id = suite.suite_id
    section.parent_id = parent.section_id + 1
    with pytest.raises(ValueError) as exc_info:
        section.link(suite=suite, parent=parent)
    assert str(exc_info.value) == \
           f"section.parent_id ({section.parent_id}) does not match parent.section_id ({parent.section_id})"


def test_case_suite_linking_fails_if_ids_unequal():
    suite = TestRailSuite.from_data(get_suite_response())
    case = TestRailCase.from_data(get_case_response())
    case.suite_id = suite.suite_id + 1
    with pytest.raises(ValueError) as exc_info:
        case.link(suite=suite)
    assert str(exc_info.value) == \
           f"case.suite_id ({case.suite_id}) does not match suite.suite_id ({suite.suite_id})"


def test_case_section_linking_fails_if_ids_unequal():
    suite = TestRailSuite.from_data(get_suite_response())
    section = TestRailSection.from_data(get_section_response())
    case = TestRailCase.from_data(get_case_response())
    case.suite_id = suite.suite_id
    case.section_id = section.section_id + 1
    with pytest.raises(ValueError) as exc_info:
        case.link(suite=suite, section=section)
    assert str(exc_info.value) == \
           f"case.section_id ({case.section_id}) does not match section.section_id ({section.section_id})"


def test_case_section_linking_passes_with_no_section():
    suite = TestRailSuite.from_data(get_suite_response())
    section = None
    case = TestRailCase.from_data(get_case_response())
    case.suite_id = suite.suite_id
    case.link(suite=suite, section=section)
    assert case.suite is suite
    assert case.section is None


def test_case_get_custom_raises_exceptions():
    case = TestRailCase.from_data(get_case_response())
    with pytest.raises(ValueError) as value_error:
        case.__getattr__('')
    assert str(value_error.value) == "Attribute must be non-zero length"
    with pytest.raises(AttributeError) as attr_error:
        case.__getattr__('does_not_exist')
    assert str(attr_error.value) == "TestRailCase instance has no custom field: 'custom_does_not_exist'"


def test_case_to_dict_returns_original_api_response():
    api_response = get_case_response()
    case = TestRailCase.from_data(api_response)
    assert case.to_dict() == api_response


def test_get_case_types_returns_correct_instance_type(mock_api_client, stats_fixture):
    subject = TestRailAPIObjectBuilder(api_client=mock_api_client, stats=stats_fixture)
    actual = subject.get_case_types()
    assert len(actual) == 2
    assert isinstance(actual, list)
    for case_type in actual:
        assert isinstance(case_type, TestRailCaseType)
    assert subject.stats.get_case_types == 1
    assert subject.stats.total == 1


def test_unlink_case_disassociates_from_suite_and_section():
    suite = TestRailSuite.from_data(get_suite_response())
    case = TestRailCase.from_data(get_case_response())
    section = TestRailSection.from_data(get_section_response())
    case.suite_id = suite.suite_id
    section.suite_id = suite.suite_id
    case.section_id = section.section_id
    section.link(suite=suite, parent=None)
    case.link(suite=suite, section=section)
    assert case.case_id in suite.cases
    assert case.case_id in section.cases
    assert case.section_id in suite.sections
    assert case.suite is suite
    assert case.section is section
    case.unlink()
    assert case.case_id not in suite.cases
    assert case.suite is None
    assert case.section is None


def test_unlink_case_on_unlinked_case_makes_no_change():
    case = TestRailCase.from_data(get_case_response())
    case.unlink()
    assert case.suite is None
    assert case.section is None
