from .conftest import *


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


def test_unlink_on_unlinked_case_makes_no_change():
    case = TestRailCase.from_data(get_case_response())
    assert case.suite is None
    assert case.section is None
    case.unlink()
    assert case.suite is None
    assert case.section is None


def test_unlink_on_unlinked_section_makes_no_change():
    section = TestRailSection.from_data(get_section_response())
    assert section.suite is None
    assert section.parent is None
    assert len(section.cases) == 0
    section.unlink()
    assert section.suite is None
    assert section.parent is None
    assert len(section.cases) == 0
