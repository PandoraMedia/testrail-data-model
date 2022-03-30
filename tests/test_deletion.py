from typing import Generator
from unittest.mock import call

from .conftest import *

from testrail_data_model.deletion import DeletionHandler, MarkForDeletionHandler, deletion_handler_factory
from testrail_data_model.model import TestRailSuite, TestRailCase, TestRailSection


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
def test_real_handler_deletes_a_single_case(mock_api_client, stats_fixture, suite_fixture, soft):
    subject = DeletionHandler(suite=suite_fixture, api_client=mock_api_client, stats=stats_fixture, soft=soft)
    case = list(suite_fixture.cases.values())[0]
    subject.delete_case(case=case)
    mock_api_client.cases.delete_case.assert_called_once_with(case_id=case.case_id, soft=int(soft))
    assert subject.stats.delete_case == 1
    assert subject.stats.total == 1
    if soft:
        assert case.case_id in suite_fixture.cases
    else:
        assert case.case_id not in suite_fixture.cases


@pytest.mark.parametrize("soft", [True, False])
def test_real_handler_deletes_a_single_section(mock_api_client, stats_fixture, suite_fixture, soft):
    subject = DeletionHandler(suite=suite_fixture, api_client=mock_api_client, stats=stats_fixture, soft=soft)
    section = list(suite_fixture.sections.values())[0]
    subject.delete_section(section=section)
    mock_api_client.sections.delete_section.assert_called_once_with(section_id=section.section_id, soft=int(soft))
    assert subject.stats.delete_section == 1
    assert subject.stats.total == 1
    if soft:
        assert section.section_id in suite_fixture.sections
    else:
        assert section.section_id not in suite_fixture.sections


@pytest.mark.parametrize("soft", [True, False])
def test_real_handler_deletes_multiple_cases(mock_api_client, stats_fixture, suite_fixture, soft):
    subject = DeletionHandler(suite=suite_fixture, api_client=mock_api_client, stats=stats_fixture, soft=soft)
    cases_to_delete = list(suite_fixture.cases.values())
    actual = subject.delete_cases(cases_to_delete)
    assert isinstance(actual, Generator)
    for _ in actual:
        continue
    expected_calls = [call(case_id=case.case_id, soft=int(soft)) for case in cases_to_delete]
    mock_api_client.cases.delete_case.assert_has_calls(calls=expected_calls, any_order=True)
    remaining_case_count = 2 if soft else 0
    assert len(suite_fixture.cases) == remaining_case_count
    assert stats_fixture.delete_case == 2
    assert stats_fixture.total == 2


@pytest.mark.parametrize("soft", [True, False])
def test_real_handler_deletes_multiple_sections(mock_api_client, stats_fixture, suite_fixture, soft):
    subject = DeletionHandler(suite=suite_fixture, api_client=mock_api_client, stats=stats_fixture, soft=soft)
    sections_to_delete = list(suite_fixture.sections.values())
    actual = subject.delete_sections(sections_to_delete)
    assert isinstance(actual, Generator)
    for _ in actual:
        continue
    expected_calls = [call(section_id=section.section_id, soft=int(soft)) for section in sections_to_delete]
    mock_api_client.sections.delete_section.assert_has_calls(calls=expected_calls, any_order=True)
    remaining_section_count = 2 if soft else 0
    assert len(suite_fixture.sections) == remaining_section_count
    assert stats_fixture.delete_section == 2
    assert stats_fixture.total == 2


def test_mark_case_for_deletion_handles_single_case(mock_api_client, stats_fixture, suite_fixture_with_deletion_marking):
    suite = suite_fixture_with_deletion_marking
    new_case = TestRailCase.from_data(get_case_response())
    new_case.suite_id = suite.suite_id
    builder = MagicMock(
        update_case=MagicMock(return_value=new_case)
    )
    subject = MarkForDeletionHandler(suite=suite, builder=builder, api_client=mock_api_client)
    new_section_id = subject.to_be_deleted_sections[0].section_id
    new_case.section_id = new_section_id
    case = list(suite.cases.values())[0]
    actual = subject.delete_case(case=case)
    assert actual is new_case
    builder.update_case.assert_called_once_with(case=case, section_id=new_section_id)


def test_mark_section_for_deletion_handles_single_section(mock_api_client, stats_fixture,
                                                          suite_fixture_with_deletion_marking):
    suite = suite_fixture_with_deletion_marking
    subject = MarkForDeletionHandler(suite=suite, builder=MagicMock(), api_client=mock_api_client)
    new_section_id = subject.to_be_deleted_sections[1].section_id
    section = None
    for _section in suite.direct_sections.values():
        if not _section.path.startswith('__to_be_deleted__'):
            section = _section
            break
    assert section is not None
    actual = subject.delete_section(section=section)
    assert actual is section
    mock_api_client.sections.move_section.assert_called_once_with(
        section_id=section.section_id,
        parent_id=new_section_id
    )


def test_mark_cases_for_deletion_handles_multiple_cases(mock_api_client, stats_fixture,
                                                        suite_fixture_with_deletion_marking):
    suite = suite_fixture_with_deletion_marking
    already_marked = TestRailCase.from_data(get_case_response())
    already_marked.suite_id = suite.suite_id
    new_case = TestRailCase.from_data(get_case_response())
    new_case.suite_id = suite.suite_id
    builder = MagicMock(
        update_case=MagicMock(side_effect=[new_case, already_marked])
    )
    subject = MarkForDeletionHandler(suite=suite, builder=builder, api_client=mock_api_client)
    new_section_id = subject.to_be_deleted_sections[0].section_id
    already_marked.section_id = new_section_id
    new_case.section_id = new_section_id
    already_marked.link(suite=suite, section=subject.to_be_deleted_sections[0])
    cases_to_delete = [list(suite.cases.values())[0], already_marked]
    actual = subject.delete_cases(cases_to_delete)
    assert isinstance(actual, Generator)
    results = [res for res in actual]
    builder.update_case.assert_called_once_with(case=cases_to_delete[0], section_id=new_section_id)
    assert len(results) == 2
    assert results == [new_case, already_marked]


def test_mark_sections_for_deletion_handles_multiple_sections(mock_api_client, stats_fixture,
                                                              suite_fixture_with_deletion_marking):
    suite = suite_fixture_with_deletion_marking
    subject = MarkForDeletionHandler(suite=suite, builder=MagicMock(), api_client=mock_api_client)
    new_section_id = subject.to_be_deleted_sections[1].section_id
    all_sections = list(suite.sections.values())
    sections_to_mark = sorted(
        [section for section in all_sections if not section.path.startswith('__to_be_deleted__')],
        key=lambda x: x.path,
        reverse=True
    )
    expected_calls = [call(section_id=section.section_id, parent_id=new_section_id) for section in sections_to_mark]
    for section in sections_to_mark:
        print(section.path)
    actual = subject.delete_sections(sections=(sections_to_mark + list(subject.to_be_deleted_sections)))
    assert isinstance(actual, Generator)
    results = [res for res in actual]
    assert len(results) > 2
    mock_api_client.sections.move_section.assert_has_calls(calls=expected_calls, any_order=False)


@pytest.mark.parametrize("settings", [{"mark_for_deletion": True}, {"mark_for_deletion": False}, {}])
def test_handler_factory_returns_correct_instance(suite_fixture, mock_api_client, settings):
    actual = deletion_handler_factory(suite=suite_fixture, api_client=mock_api_client, **settings)
    expected_type = MarkForDeletionHandler if settings.get("mark_for_deletion", True) else DeletionHandler
    assert isinstance(actual, expected_type)


def test_mark_for_deletion_special_sections_are_created_if_not_found(suite_fixture, mock_api_client):
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
    builder = MagicMock(
        create_new_section_for_path=MagicMock(side_effect=[to_be_deleted_section, to_be_deleted_section_section])
    )
    subject = MarkForDeletionHandler(suite=suite, builder=builder, api_client=mock_api_client,
                                     to_be_deleted_section_name=to_be_deleted_section_name)
    expected_calls = [call(suite, to_be_deleted_section_name), call(suite, to_be_deleted_section_name + "/sections")]
    assert subject.to_be_deleted_sections == (to_be_deleted_section, to_be_deleted_section_section)
    builder.create_new_section_for_path.assert_has_calls(calls=expected_calls, any_order=False)
