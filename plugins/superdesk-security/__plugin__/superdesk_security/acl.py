'''
Created on Jan 15, 2013

@package: superdesk security
@copyright: 2012 Sourcefabric o.p.s.
@license: http://www.gnu.org/licenses/gpl-3.0.txt
@author: Gabriel Nistor

Provides the acl setup.
'''
#TODO: move to config.
#from ..acl import acl
#from ..acl.gui import defaultRight, updateDefault
#from acl.spec import Filter
#from ally.container import ioc, support
#from ally.support.util import ref
#from gui.action.api.action import IActionManagerService
#from superdesk.security.api.authentication import IAuthenticationService
#from superdesk.security.api.filter_authenticated import Authenticated, \
#    IAuthenticatedFilterService
#from superdesk.security.api.user_action import IUserActionService
#from superdesk.user.api.user import User, IUserService
#
## --------------------------------------------------------------------
#
#@ioc.entity
#def filterAuthenticated() -> Filter:
#    '''
#    Provides filtering for the authenticated user.
#    '''
#    return Filter(1, Authenticated.Id, User.Id, support.entityFor(IAuthenticatedFilterService))
#
## --------------------------------------------------------------------
#
#@ioc.replace(updateDefault)
#def updateFilteredDefaults():
#    defaultRight().allGet(IUserActionService, filter=filterAuthenticated())
#    # Provides access for performing login
#    defaultRight().add(ref(IAuthenticationService).requestLogin, ref(IAuthenticationService).performLogin)
#    # Provides read only access to the logged in user
#    defaultRight().add(ref(IUserService).getById, filter=filterAuthenticated())
#
#@acl.setupAlternate
#def updateAlternates():
#    acl.aclAlternate(ref(IActionManagerService).getAll, ref(IUserActionService).getAll)
