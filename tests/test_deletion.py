from typing import Generator

from testrail_data_model.deletion import DeletionHandler, MarkForDeletionHandler, deletion_handler_factory

from .conftest import *


@pytest.fixture()
def mock_adapter():
    return MagicMock()


@pytest.fixture
def suite_fixture_with_deletion_marking(suite_fixture):
    to_be_deleted = TestRailSection.from_data(get_section_response())
    to_be_deleted.name = "__to_be_deleted__"
    to_be_deleted.suite_id = suite_fixture.suite_id
    to_be_deleted.parent_id = None

    to_be_deleted_sections = TestRailSection.from_data(get_section_response())
    to_be_deleted_sections.name = "sections"
    to_be_deleted_sections.suite_id = suite_fixture.suite_id
    to_be_deleted_sections.parent_id = to_be_deleted.section_id

    to_be_deleted.link(suite=suite_fixture, parent=None)
    to_be_deleted_sections.link(suite=suite_fixture, parent=to_be_deleted)
    return suite_fixture


@pytest.mark.parametrize("soft", [True, False])
def test_handler_deletes_a_single_case(mock_adapter, suite_fixture, soft):
    subject = DeletionHandler(suite=suite_fixture, adapter=mock_adapter, soft=soft)
    case = list(suite_fixture.cases.values())[0]
    subject.delete_case(case=case)
    mock_adapter.delete_case.assert_called_once_with(case=case, soft=soft)


@pytest.mark.parametrize("soft", [True, False])
def test_handler_deletes_a_single_section(mock_adapter, suite_fixture, soft):
    subject = DeletionHandler(suite=suite_fixture, adapter=mock_adapter, soft=soft)
    section = list(suite_fixture.sections.values())[0]
    subject.delete_section(section=section)
    mock_adapter.delete_section.assert_called_once_with(section=section, soft=soft)


@pytest.mark.parametrize("soft", [True, False])
def test_handler_deletes_multiple_cases(mock_adapter, suite_fixture, soft):
    subject = DeletionHandler(suite=suite_fixture, adapter=mock_adapter, soft=soft)
    cases_to_delete = list(suite_fixture.cases.values())
    actual = subject.delete_cases(cases_to_delete)
    assert isinstance(actual, Generator)
    for _ in actual:
        continue
    expected_calls = [call(case=case, soft=soft) for case in cases_to_delete]
    mock_adapter.delete_case.assert_has_calls(calls=expected_calls, any_order=False)


@pytest.mark.parametrize("soft", [True, False])
def test_handler_deletes_multiple_sections(mock_adapter, suite_fixture, soft):
    subject = DeletionHandler(suite=suite_fixture, adapter=mock_adapter, soft=soft)
    sections_to_delete = list(suite_fixture.sections.values())
    actual = subject.delete_sections(sections_to_delete)
    assert isinstance(actual, Generator)
    for _ in actual:
        continue
    expected_calls = [call(section=section, soft=soft) for section in sections_to_delete]
    mock_adapter.delete_section.assert_has_calls(calls=expected_calls, any_order=False)


def test_mark_case_for_deletion_handles_single_case(mock_adapter, suite_fixture_with_deletion_marking):
    suite = suite_fixture_with_deletion_marking
    new_case = TestRailCase.from_data(get_case_response())
    new_case.suite_id = suite.suite_id
    subject = MarkForDeletionHandler(suite=suite, adapter=mock_adapter)
    new_section_id = subject.to_be_deleted_sections[0].section_id
    new_case.section_id = new_section_id
    case = list(suite.cases.values())[0]
    mock_adapter.update_case = MagicMock(return_value=new_case)
    actual = subject.delete_case(case=case)
    assert actual is new_case
    mock_adapter.update_case.assert_called_once_with(case=case, section_id=new_section_id)


def test_mark_section_for_deletion_handles_single_section(mock_adapter, suite_fixture_with_deletion_marking):
    suite = suite_fixture_with_deletion_marking
    subject = MarkForDeletionHandler(suite=suite, adapter=mock_adapter)
    _, new_parent = subject.to_be_deleted_sections
    section = None
    for _section in suite.direct_sections.values():
        if not _section.path.startswith('__to_be_deleted__'):
            section = _section
            break
    assert section is not None

    mock_adapter.move_section = MagicMock(return_value=section)
    actual = subject.delete_section(section=section)
    assert actual is section
    mock_adapter.move_section.assert_called_once_with(section=section, new_parent=new_parent)


def test_mark_cases_for_deletion_handles_multiple_cases(mock_adapter, suite_fixture_with_deletion_marking):
    suite = suite_fixture_with_deletion_marking
    already_marked = TestRailCase.from_data(get_case_response())
    already_marked.suite_id = suite.suite_id
    new_case = TestRailCase.from_data(get_case_response())
    new_case.suite_id = suite.suite_id
    subject = MarkForDeletionHandler(suite=suite, adapter=mock_adapter)
    to_be_deleted_section = subject.to_be_deleted_sections[0]
    new_section_id = to_be_deleted_section.section_id
    already_marked.section_id = new_section_id
    new_case.section_id = new_section_id
    already_marked.link(suite=suite, section=to_be_deleted_section)
    cases_to_delete = [list(suite.cases.values())[0], already_marked]
    mock_adapter.update_case = MagicMock(return_value=new_case)
    actual = subject.delete_cases(cases_to_delete)
    assert isinstance(actual, Generator)
    results = [res for res in actual]
    mock_adapter.update_case.assert_called_once_with(case=cases_to_delete[0], section_id=new_section_id)
    assert len(results) == 2
    assert results == [new_case, already_marked]


def test_mark_sections_for_deletion_handles_multiple_sections(mock_adapter, suite_fixture_with_deletion_marking):
    suite = suite_fixture_with_deletion_marking
    subject = MarkForDeletionHandler(suite=suite, adapter=mock_adapter)
    _, new_parent = subject.to_be_deleted_sections
    all_sections = list(suite.sections.values())
    sections_to_mark = sorted(
        [section for section in all_sections if not section.path.startswith('__to_be_deleted__')],
        key=lambda x: x.path,
        reverse=True
    )
    expected_calls = [call(section=section, new_parent=new_parent) for section in sections_to_mark]
    actual = subject.delete_sections(sections=(sections_to_mark + list(subject.to_be_deleted_sections)))
    assert isinstance(actual, Generator)
    results = [res for res in actual]
    assert len(results) > 2
    mock_adapter.move_section.assert_has_calls(calls=expected_calls, any_order=False)


@pytest.mark.parametrize("settings", [{"mark_for_deletion": True}, {"mark_for_deletion": False}, {}])
def test_handler_factory_returns_correct_instance(suite_fixture, mock_adapter, settings):
    actual = deletion_handler_factory(suite=suite_fixture, adapter=mock_adapter, **settings)
    expected_type = MarkForDeletionHandler if settings.get("mark_for_deletion", True) else DeletionHandler
    assert isinstance(actual, expected_type)


def test_mark_for_deletion_special_sections_are_created_if_not_found(mock_adapter, suite_fixture):
    suite = suite_fixture
    to_be_deleted_section_name = FIELD('word')
    to_be_deleted_section = TestRailSection.from_data(get_section_response())
    to_be_deleted_section.suite_id = suite_fixture.suite_id
    to_be_deleted_section.parent_id = None
    to_be_deleted_section.name = to_be_deleted_section_name
    to_be_deleted_section_section = TestRailSection.from_data(get_section_response())
    to_be_deleted_section_section.suite_id = suite_fixture.suite_id
    to_be_deleted_section_section.parent_id = to_be_deleted_section.section_id
    to_be_deleted_section_section.name = "sections"
    mock_adapter.create_new_section_for_path = MagicMock(
        side_effect=[to_be_deleted_section, to_be_deleted_section_section]
    )
    subject = MarkForDeletionHandler(suite=suite, adapter=mock_adapter,
                                     to_be_deleted_section_name=to_be_deleted_section_name)
    expected_calls = [call(suite, to_be_deleted_section_name), call(suite, to_be_deleted_section_name + "/sections")]
    assert subject.to_be_deleted_sections == (to_be_deleted_section, to_be_deleted_section_section)
    mock_adapter.create_new_section_for_path.assert_has_calls(calls=expected_calls, any_order=False)
