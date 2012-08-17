'''
Created on July 10, 2012

@package: ally authentication
@copyright: 2012 Sourcefabric o.p.s.
@license: http://www.gnu.org/licenses/gpl-3.0.txt
@author: Mugur Rus

Provides authentication register function.
'''

from __setup__.ally_authentication_http.processor import authenticators
from ally.api.operator.authentication.service import IAuthenticationSupport
from ally.container.ioc import activate, deactivate
import ally_deploy_application

# --------------------------------------------------------------------

def registerAuthentication(support):
    assert isinstance(support, IAuthenticationSupport), 'Invalid support %s' % support

    activate(ally_deploy_application.assembly)
    authenticators().append(support)
    deactivate()
