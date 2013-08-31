'''
Created on Jan 21, 2013

@package: superdesk security
@copyright 2011 Sourcefabric o.p.s.
@license http://www.gnu.org/licenses/gpl-3.0.txt
@author: Gabriel Nistor

API for user rbac services.
'''

from ally.api.config import service
from security.rbac.core.api.rbac import IRbacPrototype
from superdesk.user.api.user import User

# --------------------------------------------------------------------

@service(('RBAC', User))
class IUserRbacService(IRbacPrototype):
    '''
    Provides the user RBAC service.
    '''
