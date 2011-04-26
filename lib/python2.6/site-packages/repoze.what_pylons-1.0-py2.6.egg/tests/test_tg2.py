# -*- coding: utf-8 -*-
##############################################################################
#
# Copyright (c) 2009, Gustavo Narea <me@gustavonarea.net>.
# All Rights Reserved.
#
# This software is subject to the provisions of the BSD-like license at
# http://www.repoze.org/LICENSE.txt.  A copy of the license should accompany
# this distribution.  THIS SOFTWARE IS PROVIDED "AS IS" AND ANY AND ALL
# EXPRESS OR IMPLIED WARRANTIES ARE DISCLAIMED, INCLUDING, BUT NOT LIMITED TO,
# THE IMPLIED WARRANTIES OF TITLE, MERCHANTABILITY, AGAINST INFRINGEMENT, AND
# FITNESS FOR A PARTICULAR PURPOSE.
#
##############################################################################
"""
Tests for this plugin when used in TurboGears 2.

"""

from tests.fixture.tg2app import BasicTGController, SecurePanel, \
                                 SecurePanelWithHandler

from base_tests import ActionDecoratorTestCase, ControllerDecoratorTestCase, \
                       ControllerDecoratorWithHandlerTestCase, \
                       TestWSGIController, EvaluatorsTestCase, TestBooleanizer


class BaseTG2Tester(TestWSGIController):
    """Base test case for TG2 controllers"""
    controller = BasicTGController


class TestActionDecoratorInTG2(ActionDecoratorTestCase, BaseTG2Tester):
    """Test case for @ActionDecoratorTestCase decorator"""
    pass


class TestControllerDecoratorInTG2(ControllerDecoratorTestCase, BaseTG2Tester):
    """Test case for @ControllerDecoratorTestCase decorator"""
    controller = SecurePanel


class TestControllerDecoratorWithHandlerInTG2(
    ControllerDecoratorWithHandlerTestCase, BaseTG2Tester):
    """Test case for @ControllerDecoratorTestCase decorator"""
    controller = SecurePanelWithHandler


class TestEvaluatorsInTG2(EvaluatorsTestCase, BaseTG2Tester):
    """Test case for predicate evaluators"""
    pass


class TestBooleanizerInTG2(TestBooleanizer, BaseTG2Tester):
    """Test case for the predicate booleanizer"""
    
    def tearDown(self):
        TestBooleanizer.tearDown(self)
        BaseTG2Tester.tearDown(self)
