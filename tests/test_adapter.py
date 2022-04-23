from typing import Generator

from .conftest import *


@pytest.fixture()
def subject_adapter(mock_api_client, stats_fixture):
    subject = TestRailAPIAdapter(api_client=mock_api_client, stats=stats_fixture)
    return subject


def test_get_project_returns_correct_instance_type(subject_adapter, mock_api_client):
    project_id = FIELD("integer_number", start=1, end=1000)
    actual = subject_adapter.get_project(project_id=project_id)
    mock_api_client.projects.get_project.assert_called_once_with(project_id=project_id)
    assert isinstance(actual, TestRailProject)
    assert actual.announcement is not None
    assert subject_adapter.stats.get_project == 1
    assert subject_adapter.stats.total == 1


def test_get_projects_returns_generator_of_project_instances(subject_adapter, mock_api_client):
    actual = subject_adapter.get_projects(limit=1)
    assert isinstance(actual, Generator)
    for project in actual:
        assert isinstance(project, TestRailProject)
        assert project.announcement is not None
    expected_calls = [call(limit=1, offset=i) for i in range(4)]
    mock_api_client.projects.get_projects.assert_has_calls(calls=expected_calls, any_order=False)
    assert subject_adapter.stats.get_projects == 4
    assert subject_adapter.stats.total == 4


def test_get_suite_returns_correct_instance_type(subject_adapter, mock_api_client):
    suite_id = FIELD("integer_number", start=1, end=1000)
    actual = subject_adapter.get_suite(suite_id=suite_id)
    mock_api_client.suites.get_suite.assert_called_once_with(suite_id=suite_id)
    assert isinstance(actual, TestRailSuite)
    assert actual.description is not None
    assert subject_adapter.stats.get_suite == 1
    assert subject_adapter.stats.total == 1


def test_get_suites_returns_list_of_suite_instances(subject_adapter, mock_api_client):
    project_id = FIELD("integer_number", start=1, end=1000)
    actual = subject_adapter.get_suites(project_id=project_id)
    assert len(actual) > 0
    for suite in actual:
        assert isinstance(suite, TestRailSuite)
        assert suite.description is not None
    mock_api_client.suites.get_suites.assert_called_once_with(project_id=project_id)
    assert subject_adapter.stats.get_suites == 1
    assert subject_adapter.stats.total == 1


def test_get_sections_returns_correct_instance_type(subject_adapter, mock_api_client):
    section_id = FIELD("integer_number", start=1, end=1000)
    actual = subject_adapter.get_section(section_id=section_id)
    mock_api_client.sections.get_section.assert_called_once_with(section_id=section_id)
    assert isinstance(actual, TestRailSection)
    assert actual.description is not None
    assert subject_adapter.stats.get_section == 1
    assert subject_adapter.stats.total == 1


def test_get_section_returns_generator_of_sections(subject_adapter, mock_api_client):
    project_id = FIELD("integer_number", start=1, end=1000)
    suite_id = FIELD("integer_number", start=1, end=1000)
    actual = subject_adapter.get_sections(project_id=project_id, suite_id=suite_id, limit=1, offset=0)
    for section in actual:
        assert isinstance(section, TestRailSection)
        assert section.description is not None
    expected_calls = [call(limit=1, offset=i, project_id=project_id, suite_id=suite_id) for i in range(4)]
    mock_api_client.sections.get_sections.assert_has_calls(calls=expected_calls, any_order=False)
    assert subject_adapter.stats.total == 4
    assert subject_adapter.stats.get_sections == 4


def test_add_section_returns_correct_instance_type(subject_adapter, mock_api_client):
    project_id = FIELD("integer_number", start=1, end=1000)
    suite_id = FIELD("integer_number", start=1, end=1000)
    name = FIELD("word")
    description = FIELD("text")
    parent_id = FIELD("integer_number", start=1, end=1000)
    actual = subject_adapter.add_section(
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
    assert subject_adapter.stats.add_section == 1
    assert subject_adapter.stats.total == 1


def test_get_case_returns_correct_instance_type(subject_adapter, mock_api_client):
    case_id = FIELD("integer_number", start=1, end=1000)
    actual = subject_adapter.get_case(case_id=case_id)
    assert isinstance(actual, TestRailCase)
    assert len(actual.steps_separated) == 1
    assert actual.steps_separated[0]["content"] is not None
    assert subject_adapter.stats.get_case == 1
    assert subject_adapter.stats.total == 1
    mock_api_client.cases.get_case.assert_called_once_with(case_id=case_id)


def test_add_case_returns_correct_instance_type(subject_adapter, mock_api_client):
    section_id = FIELD("integer_number", start=1, end=1000)
    title = FIELD("title")
    actual = subject_adapter.add_case(section_id=section_id, title=title)
    assert isinstance(actual, TestRailCase)
    assert len(actual.steps_separated) == 1
    assert actual.steps_separated[0]["content"] is not None
    assert subject_adapter.stats.add_case == 1
    assert subject_adapter.stats.total == 1
    mock_api_client.cases.add_case.assert_called_once_with(section_id=section_id, title=title)


def test_update_case_returns_correct_instance_type(subject_adapter, mock_api_client):
    case_id = FIELD("integer_number", start=1, end=1000)
    section_id = FIELD("integer_number", start=1, end=1000)
    title = FIELD("title")
    start_case = subject_adapter.get_case(case_id=case_id)
    actual = subject_adapter.update_case(case=start_case, title=title, section_id=section_id)
    assert isinstance(actual, TestRailCase)
    assert len(actual.steps_separated) == 1
    assert actual.steps_separated[0]["content"] is not None
    assert subject_adapter.stats.update_case == 1
    assert subject_adapter.stats.total == 2
    mock_api_client.cases.update_case.assert_called_once_with(
        case_id=start_case.case_id,
        title=title,
        section_id=section_id
    )


def test_get_cases_returns_generator_of_cases(subject_adapter, mock_api_client):
    project_id = FIELD("integer_number", start=1, end=1000)
    actual = subject_adapter.get_cases(project_id=project_id, limit=2, offset=0)
    assert isinstance(actual, Generator)
    for case in actual:
        assert isinstance(case, TestRailCase)
        assert len(case.steps_separated) == 1
        assert case.steps_separated[0]["content"] is not None
    expected_calls = [call(project_id=project_id, limit=2, offset=i) for i in range(0, 4, 2)]
    mock_api_client.cases.get_cases.assert_has_calls(expected_calls, any_order=False)
    assert subject_adapter.stats.get_cases == 2
    assert subject_adapter.stats.total == 2


def test_get_cases_with_suite_returns_generator_of_cases(subject_adapter, mock_api_client):
    project_id = FIELD("integer_number", start=1, end=1000)
    suite_id = FIELD("integer_number", start=1, end=1000)
    actual = subject_adapter.get_cases(project_id=project_id, suite_id=suite_id, limit=2, offset=0)
    assert isinstance(actual, Generator)
    for case in actual:
        assert isinstance(case, TestRailCase)
        assert len(case.steps_separated) == 1
        assert case.steps_separated[0]["content"] is not None
    expected_calls = [call(project_id=project_id, suite_id=suite_id, limit=2, offset=i) for i in range(0, 4, 2)]
    mock_api_client.cases.get_cases.assert_has_calls(expected_calls, any_order=False)
    assert subject_adapter.stats.get_cases == 2
    assert subject_adapter.stats.total == 2


def test_get_case_fields_returns_correct_instance_type(subject_adapter, mock_api_client):
    actual = subject_adapter.get_case_fields()
    assert len(actual) > 0
    for field_item in actual:
        assert isinstance(field_item, TestRailCaseField)
        assert field_item.description is not None
    assert subject_adapter.stats.get_case_fields == 1
    assert subject_adapter.stats.total == 1


def test_get_case_types_returns_correct_instance_type(subject_adapter, mock_api_client):
    actual = subject_adapter.get_case_types()
    assert len(actual) == 2
    assert isinstance(actual, list)
    for case_type in actual:
        assert isinstance(case_type, TestRailCaseType)
    assert subject_adapter.stats.get_case_types == 1
    assert subject_adapter.stats.total == 1


@pytest.mark.parametrize("soft", [True, False])
def test_delete_section_deletes_a_single_section(subject_adapter, mock_api_client, suite_fixture, soft):
    section = list(suite_fixture.sections.values())[0]
    subject_adapter.delete_section(section=section, soft=soft)
    mock_api_client.sections.delete_section.assert_called_once_with(section_id=section.section_id, soft=int(soft))
    assert subject_adapter.stats.delete_section == 1
    assert subject_adapter.stats.total == 1
    if soft:
        assert section.section_id in suite_fixture.sections
    else:
        assert section.section_id not in suite_fixture.sections


@pytest.mark.parametrize("soft", [True, False])
def test_delete_case_deletes_a_single_case(subject_adapter, mock_api_client, suite_fixture, soft):
    case = list(suite_fixture.cases.values())[0]
    subject_adapter.delete_case(case=case, soft=soft)
    mock_api_client.cases.delete_case.assert_called_once_with(case_id=case.case_id, soft=int(soft))
    assert subject_adapter.stats.delete_case == 1
    assert subject_adapter.stats.total == 1
    if soft:
        assert case.case_id in suite_fixture.cases
    else:
        assert case.case_id not in suite_fixture.cases


def test_move_section_moves_a_single_section_to_top(subject_adapter, mock_api_client, suite_fixture):
    new_parent = None
    top_section = list(suite_fixture.direct_sections.values())[0]
    bottom_section = list(top_section.sections.values())[0]
    assert bottom_section.parent is not None
    subject_adapter.move_section(section=bottom_section, new_parent=new_parent)
    assert bottom_section.parent is None
    mock_api_client.sections.move_section.assert_called_once_with(section_id=bottom_section.section_id, parent_id=None)


def test_move_section_moves_a_single_section_to_new_section(subject_adapter, mock_api_client, suite_fixture):
    top_section = list(suite_fixture.direct_sections.values())[0]
    bottom_section = list(top_section.sections.values())[0]
    new_parent = TestRailSection.from_data(get_section_response())
    new_parent.suite_id = suite_fixture.suite_id
    new_parent.link(suite_fixture)
    assert bottom_section.parent is top_section
    subject_adapter.move_section(section=bottom_section, new_parent=new_parent)

    assert bottom_section.parent is not top_section
    assert bottom_section.parent is new_parent
    mock_api_client.sections.move_section.assert_called_once_with(section_id=bottom_section.section_id,
                                                                  parent_id=new_parent.section_id)


def test_create_new_section_for_path(subject_adapter):
    suite = TestRailSuite.from_data(get_suite_response())
    new_section = TestRailSection.from_data(get_section_response())
    parent_section = TestRailSection.from_data(get_section_response())

    # Set up ID (foreign key) links without explicitly linking objects
    new_section.suite_id = suite.suite_id
    parent_section.suite_id = suite.suite_id
    new_section.parent_id = parent_section.section_id

    with patch.object(suite, 'section_for_path', return_value=parent_section) as section_for_path_mock:
        with patch.object(subject_adapter, 'add_section', return_value=new_section) as add_section_patch:
            actual = subject_adapter.create_new_section_for_path(suite=suite, path='path/to/new/section')

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