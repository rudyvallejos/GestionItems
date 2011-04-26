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
Fake controller-only TG2 application.

"""

from tg import response
from tg.controllers import TGController
from tg.decorators import expose

from repoze.what.predicates import All, Not, not_anonymous, is_user, in_group
from repoze.what.plugins.pylonshq import ActionProtector, ControllerProtector,\
                                         is_met, not_met

from tests.fixture import special_require


class SubController1(TGController):
    """Mock TG2 subcontroller"""
    
    @expose()
    def index(self):
        return 'hello sub1'
    
    @expose()
    def in_group(self):
        return 'in group'


class SecurePanel(TGController):
    """Mock TG2 secure controller"""
    
    @expose()
    def index(self):
        return 'you are in the panel'
    
    @expose()
    @ActionProtector(in_group('developers'))
    def commit(self):
        return 'you can commit'
SecurePanel = ControllerProtector(in_group('admins'))(SecurePanel)


class SecurePanelWithHandler(TGController):
    """Mock TG2 secure controller"""
    
    @expose()
    def index(self):
        return 'you are in the panel with handler'
    
    @staticmethod
    def sorry(reason):
        response.status = 200
        return 'what are you doing here? %s' % reason
SecurePanelWithHandler = ControllerProtector(
    in_group('admins'), 'sorry')(SecurePanelWithHandler)

class BasicTGController(TGController):
    """Mock TG2 controller"""

    sub1 = SubController1()
    
    panel = SecurePanel()
    
    @expose()
    def index(self, **kwargs):
        return 'hello world'
    
    # In v1.0b1, if @ActionProtector was before @expose then the action was not
    # found
    @ActionProtector(in_group('admins'))
    @expose()
    def admin(self):
        return 'got to admin'
    
    def troll_detected(reason):
        # Let's ignore the reason
        return 'Trolls are banned'
    
    @expose()
    @ActionProtector(All(not_anonymous(), Not(is_user('sballmer'))),
                     denial_handler=troll_detected)
    def leave_comment(self):
        return 'Comment accepted'
    
    @expose()
    @special_require(not_anonymous())
    def logout(self):
        return 'You have been logged out'
    
    @expose()
    @special_require(All(not_anonymous(), Not(is_user('sballmer'))),
                     denial_handler=troll_detected)
    def start_thread(self):
        return 'You have started a thread'
    
    @expose()
    @ActionProtector(Not(not_anonymous()))
    def get_parameter(self, something):
        # Checking that parameters are received
        return 'Parameter received: %s' % something
    
    @expose()
    def boolean_predicate(self):
        p = not_anonymous()
        return 'The predicate is %s' % bool(p)
    
    @expose()
    def is_met_util(self):
        if is_met(not_anonymous()):
            return 'You are not anonymous'
        return 'You are anonymous'
    
    @expose()
    def not_met_util(self):
        if not_met(not_anonymous()):
            return 'You are anonymous'
        return 'You are not anonymous'
