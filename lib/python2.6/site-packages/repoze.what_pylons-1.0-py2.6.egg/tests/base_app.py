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

"""Stuff required to set up a Pylons/TG2 application for testing."""

import os

from paste import httpexceptions
from paste.registry import RegistryManager
from webtest import TestApp
from beaker.middleware import CacheMiddleware, SessionMiddleware

from pylons.testutil import ControllerWrap, SetupCacheGlobal

from repoze.who.plugins.auth_tkt import AuthTktCookiePlugin
from repoze.what.middleware import setup_auth
from repoze.what.adapters import BaseSourceAdapter


data_dir = os.path.dirname(os.path.abspath(__file__))
session_dir = os.path.join(data_dir, 'session')


default_environ = {
    'pylons.use_webob' : True,
    'pylons.routes_dict': dict(action='index'),
    'paste.config': dict(global_conf=dict(debug=True))
}


def make_app(controller_klass, environ={}):
    """Creates a `TestApp` instance."""

    app = ControllerWrap(controller_klass)
    app = SetupCacheGlobal(app, environ, setup_cache=True, setup_session=True)
    app = RegistryManager(app)
    app = SessionMiddleware(app, {}, data_dir=session_dir)
    app = CacheMiddleware(app, {}, data_dir=os.path.join(data_dir, 'cache'))

    # Setting up the source adapters:
    groups_adapters = {'my_groups': FakeGroupSourceAdapter()}
    permissions_adapters = {'my_permissions': FakePermissionSourceAdapter()}
    
    # Setting up repoze.who:
    cookie = AuthTktCookiePlugin('secret', 'authtkt')
    
    identifiers = [('cookie', cookie)]
    app = setup_auth(app, groups_adapters, permissions_adapters, 
                     identifiers=identifiers, authenticators=[],
                     challengers=[], skip_authentication=True)

    app = httpexceptions.make_middleware(app)
    return TestApp(app)


#{ Mock definitions


class FakeGroupSourceAdapter(BaseSourceAdapter):
    """Mock group source adapter"""

    def __init__(self):
        super(FakeGroupSourceAdapter, self).__init__()
        self.fake_sections = {
            u'admins': set([u'rms']),
            u'developers': set([u'rms', u'linus']),
            u'trolls': set([u'sballmer']),
            u'python': set(),
            u'php': set()
            }

    def _find_sections(self, identity):
        username = identity['repoze.who.userid']
        return set([n for (n, g) in self.fake_sections.items()
                    if username in g])


class FakePermissionSourceAdapter(BaseSourceAdapter):
    """Mock permissions source adapter"""

    def __init__(self):
        super(FakePermissionSourceAdapter, self).__init__()
        self.fake_sections = {
            u'see-site': set([u'trolls']),
            u'edit-site': set([u'admins', u'developers']),
            u'commit': set([u'developers'])
            }

    def _find_sections(self, group_name):
        return set([n for (n, p) in self.fake_sections.items()
                    if group_name in p])

#}
