'''
Created on July 10, 2012

@package: ally authentication
@copyright: 2012 Sourcefabric o.p.s.
@license: http://www.gnu.org/licenses/gpl-3.0.txt
@author: Mugur Rus

Provides authentication register function.
'''

# --------------------------------------------------------------------

def registerAuthentication(authenticate):
    '''
    '''
    import ally_deploy_application
    authenticationHandler = ally_deploy_application.assembly.processForPartialName('ally_authentication_http.processor.authentication')
    authenticationHandler.userKeyGenerator = authenticate
