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
Test suite for the repoze.what Pylons plugin.

This module includes miscellaneous tests.

"""

from inspect import ismethod
from unittest import TestCase

from repoze.what.plugins.pylonshq import ControllerProtector


class TestControllerDecorator(TestCase):
    """Framework-independent tests for @ControllerProtector decorator"""
    
    def test_controller_class(self):
        """The ``__before__`` method must be defined if passed a class"""
        # Creating a fake controller:
        class DaController(object): pass
        DaController = ControllerProtector(None)(DaController)
        # Testing it:
        assert hasattr(DaController, '__before__')
        assert ismethod(DaController.__before__)
    
    def test_controller_instance(self):
        """
        The ``__before__`` method must be defined if passed a class
        instance.
        
        """
        # Creating a fake controller:
        class DaController(object): pass
        da_instance = DaController()
        da_instance = ControllerProtector(None)(da_instance)
        # Testing it:
        assert hasattr(da_instance, '__before__')
        assert ismethod(da_instance.__before__)
