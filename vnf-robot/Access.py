# -*- coding: utf-8 -*-
from robot.libraries.BuiltIn import BuiltIn

import exc
from robot.api import logger, TestSuite, TestData
from robot.api.deco import keyword

from Utils import Utils
from robotlibcore import DynamicCore
from version import VERSION


class Access(DynamicCore):
    """The Access module contains keywords to validate users and groups"""

    ROBOT_LIBRARY_SCOPE = 'TEST CASE'
    __version__ = VERSION

    def __init__(self):
        DynamicCore.__init__(self, [])
        self.context = None
        self.sut = None

        logger.info(u"Importing {}".format(self.__class__))

    def run_keyword(self, name, args, kwargs):
        """
        Mandatory method for using robot dynamic libraries

        Returns:
            None
        """
        self.context = BuiltIn().get_library_instance(all=True)

        logger.info(u"\nRunning keyword '%s' with arguments %s." % (name, args), also_console=True)
        return self.keywords[name](*args, **kwargs)

    @keyword('${node:"?\S+"?} ${operator:has|has not} user ${user:"?\S+"?}')
    def user_exists(self, node=None, operator='has', user=None):
        """
        Validates that a user exists on a node.

        Args:
            operator: has or has not
            user: user name to validate
            node: node to run the check on

        Returns:
            None

        """
        user = user.strip("\"")

        self.users_exist(node=node, operator=operator, users='["{}"]'.format(user))

    @keyword('${node:"?\S+"?} ${operator:has|has not} users ${users:\[("\S+",?\s*)+\]}')
    def users_exist(self, node=None, operator='has', users=None):
        """
        Validates that a list of user exists (or does not exist) on a node.

        Args:
            operator: has or has not
            users: user name to validate
            node: node to run the check on

        Returns:
            None

        """
        if users is None:
            users = []

        Utils.validate_list(u'user', users)
        Utils.validate_string(u'operator', operator)
        Utils.validate_argument(u'node', node)

    @keyword('${node:"?\S+"?} ${operator:has|has not} user ${user:"?\S+"?} with properties ${props:{[^\}]+\}}')
    def user_has_properties(self, node=None, operator='has', user=None, props=None):
        """
        Validates that a list of user exists (or does not exist) on a node.

        Args:
            props: Properties to validate: uid, gid, groups, home, shell
            operator: has or has not
            user: user name to validate
            node: node to run the check on

        Returns:
            None

        """

        Utils.validate_argument(u'user', user)
        Utils.validate_string(u'operator', operator)
        Utils.validate_argument(u'node', node)
        Utils.validate_json(u'props', props)

    @keyword('${node:"?\S+"?} ${operator:has|has not} group ${group:"?\S+"?}')
    def group_exists(self, node=None, operator='has', group=None):
        """
        Validates that a group exists on a node.

        Args:
            operator: has or has not
            group: user name to validate
            node: node to run the check on

        Returns:
            None

        """
        group = group.strip("\"")

        self.groups_exist(node=node, operator=operator, groups='["{}"]'.format(group))

    @keyword('${node:"?\S+"?} ${operator:has|has not} groups ${groups:\[("\S+",?\s*)+\]}')
    def groups_exist(self, node=None, operator='has', groups=None):
        """
        Validates that a list of groups exists (or does not exist) on a node.

        Args:
            operator: has or has not
            groups: user name to validate
            node: node to run the check on

        Returns:
            None

        """
        if groups is None:
            groups = []

        Utils.validate_list(u'groups', groups)
        Utils.validate_string(u'operator', operator)
        Utils.validate_argument(u'node', node)

    @keyword('${node:"?\S+"?} ${operator:has|has not} group ${group:"?\S+"?} with properties ${props:{[^\}]+\}}')
    def group_has_properties(self, node=None, operator='has', group=None, props=None):
        """
        Validates that a list of user exists (or does not exist) on a node.

        Args:
            props: Properties to validate: uid, gid, groups, home, shell
            operator: has or has not
            group: user name to validate
            node: node to run the check on

        Returns:
            None

        """

        Utils.validate_argument(u'group', group)
        Utils.validate_string(u'operator', operator)
        Utils.validate_argument(u'node', node)
        Utils.validate_json(u'props', props)


