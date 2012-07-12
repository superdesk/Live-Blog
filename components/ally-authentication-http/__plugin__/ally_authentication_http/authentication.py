'''
Created on July 10, 2012

@package: ally authentication
@copyright: 2012 Sourcefabric o.p.s.
@license: http://www.gnu.org/licenses/gpl-3.0.txt
@author: Mugur Rus

Provides authentication register function.
'''

from ally.container.ioc import activate, deactivate
from __setup__.ally_authentication_http.processor import authentication

# --------------------------------------------------------------------

def registerAuthentication(authenticate):
    '''
    '''
    from ally_deploy_application import assembly
    activate(assembly)
    authentication().userKeyGenerator = authenticate
    deactivate()
