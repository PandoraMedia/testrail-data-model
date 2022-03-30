"""
Module for providing different ways of deleting TestRail objects (e.g. cases/sections)

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

import logging

from abc import ABC, abstractmethod
from functools import lru_cache
from typing import Tuple, List, Optional, Generator

from testrail_api import TestRailAPI

from .model import TestRailSuite, TestRailCase, TestRailSection
from .stats import TestRailAPIRequestStats
from .builder import TestRailAPIObjectBuilder

logger = logging.getLogger(__package__)


class BaseDeletionHandler(ABC):
    """
    Abstract Base Class which defines key functionality of a BaseDeletionHandler

    :param suite: Hierarchy of TestRailSection and TestRailCase instances
    :type suite: TestRailSuite
    :param api_client: TestRail client API object
    :type api_client: TestRailAPI
    :param stats: For tracking TestRail request metrics
    :type stats: TestRailAPIRequestStats
    """

    def __init__(self, suite: TestRailSuite, api_client: TestRailAPI, stats: Optional[TestRailAPIRequestStats] = None):
        """Constructor"""
        self._suite = suite
        self._api_client = api_client
        self._stats = stats or TestRailAPIRequestStats()

    @property
    def api_client(self) -> TestRailAPI:
        """
        :return: Object for interacting with the TestRail API
        :rtype: TestRailAPI
        """
        return self._api_client

    @property
    def stats(self) -> TestRailAPIRequestStats:
        """
        :return: Object tracking TestRail API request metrics
        :rtype: TestRailAPIRequestStats
        """
        return self._stats

    @abstractmethod
    def delete_section(self, section: TestRailSection):
        """
        Override this method to describe how to delete a single TestRailSection
        :param section: section to delete
        :type section: TestRailSection
        """

    @abstractmethod
    def delete_case(self, case: TestRailCase):
        """
        Override this method to describe how to delete a single TestRailCase
        :param case: case to delete
        :type case: TestRailCase
        """

    @abstractmethod
    def delete_sections(self, sections: List[TestRailSection]) -> Generator:
        """
        Override this method to describe how to delete a List[TestRailSection]

        NOTE: Deleting a high-level section in TestRail will delete its
        child sections and cases, which may save the client unnecessary time
        spent during API calls through the network.

        :param sections: sections to delete
        :type sections: List[TestRailSection]
        :return: yields results from deleting possibly multiple sections
        :rtype: Generator
        """

    @abstractmethod
    def delete_cases(self, cases: List[TestRailCase]) -> Generator:
        """
        Override this method to describe how to delete a List[TestRailCase]

        :param cases: cases to delete
        :type cases: List[TestRailCase]
        :return: yields results from deleting possibly multiple cases
        :rtype: Generator
        """


class DeletionHandler(BaseDeletionHandler):
    """
    USE WITH CAUTION!

    A deletion handler implementation which executes the real "delete" TestRail API methods.
    This is more dangerous than other implementation (e.g. ToBeDeletedDeletionHandler) because it actually
    deletes cases, and their associated history. Even re-creating the test case with the same information
    will not restore the missing information on previous test runs. Also, URLs depend on IDs, so recreating
    once-deleted test cases will not restore the old URL.

    :param suite: Hierarchy of TestRailSection and TestRailCase instances
    :type suite: TestRailSuite
    :param api_client: TestRail client API object
    :type api_client: TestRailAPI
    :param stats: For tracking TestRail request metrics
    :type stats: TestRailAPIRequestStats
    :param soft: True to not actually perform deletion, False to really perform deletion (default: False)
    :type soft: bool
    """

    def __init__(self, suite: TestRailSuite, api_client: TestRailAPI, stats: Optional[TestRailAPIRequestStats] = None,
                 soft: bool = False):
        """Constructor"""
        super().__init__(suite=suite, api_client=api_client, stats=stats)
        self._soft = soft

    @property
    def soft(self) -> bool:
        """
        :return: True if this instance adds "soft=1" to deletion API requests, False otherwise
        :rtype: bool
        """
        return self._soft

    def delete_section(self, section: TestRailSection):
        """
        Delete a single TestRailSection from TestRail

        :param section: the section to delete
        :type section: TestRailSection
        """
        logger.debug("Deleting TestRailSection: %s", section)
        self.stats.delete_section += 1
        self.api_client.sections.delete_section(section_id=section.section_id, soft=int(self.soft))
        if not self.soft:
            section.unlink()

    def delete_case(self, case: TestRailCase):
        """
        Delete a single TestRailCase from TestRail

        :param case: the case to delete
        :type case: TestRailCase
        """
        logger.debug("Deleting TestRailCase: %s", case)
        self.stats.delete_case += 1
        self.api_client.cases.delete_case(case_id=case.case_id, soft=int(self.soft))
        if not self.soft:
            case.unlink()

    def delete_sections(self, sections: List[TestRailSection]) -> Generator:
        """
        Delete a list of TestRailSection instances

        :param sections: the list of TestRailSection instances to delete
        :type sections: List[TestRailSection]
        :return: yields after deleting one section at a time
        :rtype: Generator
        """
        for idx, section in enumerate(sections):
            section_id, path = section.section_id, section.path
            logger.info("Deleting TestRailSection: (ID: %i, Path: %s) (%i/%i)", section_id, path, idx+1, len(sections))
            self.delete_section(section=section)
            yield

    def delete_cases(self, cases: List[TestRailCase]) -> Generator:
        """
        Delete a list of TestRailCase instances

        :param cases: the list of TestRailCase instances to delete
        :type cases: List[TestRailCase]
        :return: yields after deleting one case at a time
        :rtype: Generator
        """
        for idx, case in enumerate(cases):
            case_id, title = case.case_id, case.title
            logger.info("Deleting TestRailCase: (ID: %i, Title: %s) (%i/%i)", case_id, title, idx+1, len(cases))
            self.delete_case(case=case)
            yield


class MarkForDeletionHandler(BaseDeletionHandler):
    """
    Deletion handler which moves cases and sections to a special reserved section
    __to_be_deleted__, which essentially marks for future manual deletion.

    This also allows test cases to be easily restored in a way which preserves their
    IDs, which preserves links and test result history.

    :param suite: Hierarchy of TestRailSection and TestRailCase instances
    :type suite: TestRailSuite
    :param builder: Used to create new TestRail API object instances
    :type builder: TestRailAPIObjectBuilder
    :param api_client: TestRail client API object
    :type api_client: TestRailAPI
    :param stats: For tracking TestRail request metrics
    :type stats: TestRailAPIRequestStats
    :param to_be_deleted_section_name: name of the special section which holds cases marked for deletion
    :type to_be_deleted_section_name: Optional[str], default None
    """

    def __init__(self, suite: TestRailSuite, builder: TestRailAPIObjectBuilder, api_client: TestRailAPI,
                 stats: Optional[TestRailAPIRequestStats] = None, to_be_deleted_section_name: Optional[str] = None):
        """Constructor"""
        super().__init__(suite=suite, api_client=api_client, stats=stats)
        self._builder = builder
        self._to_be_deleted_section_name = to_be_deleted_section_name or "__to_be_deleted__"

    def delete_section(self, section: TestRailSection) -> TestRailSection:
        """
        Mark a single section for deletion

        :param section: A TestRail section instance
        :type section: TestRailSection
        :return: The same TestRailSection instance, with possibly altered parent section
        :rtype: TestRailSection
        """
        _, to_be_deleted_sections_section = self.to_be_deleted_sections
        logger.debug("Marking section for deletion: %s", section)
        self.stats.move_section += 1
        self.api_client.sections.move_section(
            section_id=section.section_id,
            parent_id=to_be_deleted_sections_section.section_id
        )
        section.move(new_parent=to_be_deleted_sections_section)
        return section

    def delete_case(self, case: TestRailCase) -> TestRailCase:
        """
        Mark a single test case for deletion

        :param case: A test-case
        :type case: TestRailCase
        :return: a new TestRailCase object, which may have new section ID and updated_on timestamp
        :rtype: TestRailCase
        """
        to_be_deleted_section, _ = self.to_be_deleted_sections
        kwargs = {"section_id": to_be_deleted_section.section_id}
        logger.debug("Marking case for deletion: %s", case)
        moved_case = self._builder.update_case(case=case, **kwargs)
        case.unlink()
        moved_case.link(suite=self._suite, section=to_be_deleted_section)
        return moved_case

    def delete_sections(self, sections: List[TestRailSection]) -> Generator:
        """
        Mark a list of TestRailSection instances for deletion.

        :param sections: the list of TestRailSection instances to delete
        :type sections: List[TestRailSection]
        :return: yields the section which has been marked for deletion, one at a time
        :rtype: Generator
        """
        for idx, section in enumerate(sections):
            path = section.path
            section_id = section.section_id
            if not path.startswith(self._to_be_deleted_section_name):
                logger.info("Marking section for deletion: (ID: %i, Path: %s) (%i/%i)", section_id, path, idx+1,
                            len(sections))
                self.delete_section(section=section)
            else:
                logger.info("Section already marked for deletion: (ID: %i, Path: %s) (%i/%i)", section_id, path, idx+1,
                            len(sections))
            yield section

    def delete_cases(self, cases: List[TestRailCase]) -> Generator:
        """
        Mark a list of TestRailCase instances for deletion.

        :param cases: the list of TestRailCase instances to delete
        :type cases: List[TestRailCase]
        :return: yields the case which has been marked for deletion, one at a time
        :rtype: Generator
        """
        for idx, case in enumerate(cases):
            case_id = case.case_id
            title = case.title
            if not case.path.startswith(self._to_be_deleted_section_name):
                logger.info("Marking case for deletion: (ID: %i, Title: %s) (%i/%i)", case_id, title, idx+1, len(cases))
                result = self.delete_case(case=case)
            else:
                logger.info("Case already marked for deletion: (ID: %i, Title: %s) (%i/%i)", case_id, title, idx+1,
                            len(cases))
                result = case
            yield result

    @property
    @lru_cache
    def to_be_deleted_sections(self) -> Tuple[TestRailSection, TestRailSection]:
        """
        Creates the special reserved section(s) which will hold all "to-be-deleted" cases
        and sections until they are manually deleted. The result is cached so that repeated
        trips to the API or retrieving a section for a path are avoided.

        :return: first holds cases, second holds sections
        :rtype: Tuple[TestRailSection, TestRailSection]
        """
        ensure_paths = [self._to_be_deleted_section_name, self._to_be_deleted_section_name + "/sections"]
        needed_sections = []
        for path in ensure_paths:
            section = self._suite.section_for_path(path)
            if section is None:
                section = self._builder.create_new_section_for_path(self._suite, path)
            needed_sections.append(section)
        return needed_sections[0], needed_sections[1]


def deletion_handler_factory(
        suite: TestRailSuite,
        api_client: TestRailAPI,
        builder: Optional[TestRailAPIObjectBuilder] = None,
        **settings
) -> BaseDeletionHandler:
    """
    Factory function to create a child-class implementation of BaseDeletionHandler.

    :param suite: Hierarchy of TestRailSection and TestRailCase instances
    :type suite: TestRailSuite
    :param api_client: TestRail client API object
    :type api_client: TestRailAPI
    :param builder: Used to create new TestRail API object instances (default: None)
    :type builder: TestRailAPIObjectBuilder
    :param settings: kwargs for configuring additional behaviors
    :type settings: Dict
    :return: An implementation of the DeletionHandler abstract base class
    :rtype: BaseDeletionHandler
    """
    if settings.get("mark_for_deletion", True):
        builder = builder or TestRailAPIObjectBuilder(api_client=api_client)
        to_be_deleted_section_name = settings.get("mark_for_deletion_section_name", None)
        deletion_handler = MarkForDeletionHandler(suite=suite, api_client=api_client, builder=builder,
                                                  to_be_deleted_section_name=to_be_deleted_section_name)
    else:
        soft = settings.get("soft", True)
        deletion_handler = DeletionHandler(suite=suite, api_client=api_client, soft=soft)
    return deletion_handler
