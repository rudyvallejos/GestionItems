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
Tests for this plugin when used in Pylons.

"""

from tests.fixture.pylonsapp import BasicPylonsController, SecurePanel, \
                                    SecurePanelWithHandler

from base_tests import ActionDecoratorTestCase, ControllerDecoratorTestCase, \
                       ControllerDecoratorWithHandlerTestCase, \
                       TestWSGIController, EvaluatorsTestCase, TestBooleanizer


class BasePylonsTester(TestWSGIController):
    """Base test case for Pylons controllers"""
    controller = BasicPylonsController


class TestActionDecoratorInPylons(ActionDecoratorTestCase, BasePylonsTester):
    """Test case for @ActionDecoratorTestCase decorator"""
    pass


class TestControllerDecoratorInPylons(ControllerDecoratorTestCase,
                                      BasePylonsTester):
    """Test case for @ControllerDecoratorTestCase decorator"""
    controller = SecurePanel


class TestControllerDecoratorWithHandlerInPylons(
    ControllerDecoratorWithHandlerTestCase, BasePylonsTester):
    """Test case for @ControllerDecoratorTestCase decorator with handler"""
    controller = SecurePanelWithHandler


class TestEvaluatorsInPylons(EvaluatorsTestCase, BasePylonsTester):
    """Test case for predicate evaluators"""
    pass


class TestBooleanizerInPylons(TestBooleanizer, BasePylonsTester):
    """Test case for the predicate booleanizer"""
    
    def tearDown(self):
        TestBooleanizer.tearDown(self)
        BasePylonsTester.tearDown(self)
