from .conftest import *


@pytest.fixture()
def mock_adapter():
    suite = TestRailSuite.from_data(get_suite_response())
    top_section = TestRailSection.from_data(get_section_response())
    bottom_section = TestRailSection.from_data(get_section_response())
    case = TestRailCase.from_data(get_case_response())
    suite_id = suite.suite_id

    # Set up ID (foreign key) matching without explicitly linking
    top_section.suite_id = suite_id
    top_section.parent_id = None
    bottom_section.suite_id = suite_id
    bottom_section.parent_id = top_section.section_id
    case.suite_id = suite_id
    case.section_id = bottom_section.section_id

    return MagicMock(
        get_cases=MagicMock(return_value=[case]),
        get_sections=MagicMock(return_value=[top_section, bottom_section]),
        get_suite=MagicMock(return_value=suite)
    )


@pytest.fixture()
def subject_builder(mock_adapter):
    subject = TestRailAPIObjectBuilder(adapter=mock_adapter)
    return subject


def test_build_suite_returns_suite_instance_with_links(subject_builder):
    project_id = 0
    suite_id = 0
    suite = subject_builder.build_suite(project_id=project_id, suite_id=suite_id)
    assert isinstance(suite, TestRailSuite)

    # Check links from TestRailSuite object
    assert len(suite.sections) == 2
    assert len(suite.cases) == 1
    assert len(suite.direct_cases) == 0

    # Check links from top-most TestRailSection object
    top_section = list(suite.direct_sections.values())[0]
    assert len(top_section.sections) == 1
    assert len(top_section.cases) == 0
    assert top_section.suite is suite
    assert top_section.parent is None

    # Check links from bottom-most TestRailSection object
    bottom_section = list(top_section.sections.values())[0]
    assert bottom_section.parent is top_section
    assert len(bottom_section.sections) == 0
    assert len(bottom_section.cases) == 1

    # Check links from the TestRailCase object
    case = list(suite.cases.values())[0]
    assert case.suite is suite
    assert case.section is bottom_section

    # Check section paths exist
    assert suite.all_section_paths == {
        top_section.section_id: top_section.path,
        bottom_section.section_id: bottom_section.path
    }
    assert suite.section_for_path(top_section.path) is top_section
    assert suite.section_for_path(bottom_section.path) is bottom_section
    assert suite.section_for_path(bottom_section.path + "foobar") is None
    assert bottom_section.path == f"{top_section.name}/{bottom_section.name}"
    assert case.path == f"{top_section.name}/{bottom_section.name}"

    # Try unlinking
    case.unlink()
    top_section.unlink()

    assert len(suite.cases) == 0
    assert len(suite.sections) == 0
    assert len(top_section.sections) == 0
    assert len(bottom_section.cases) == 0