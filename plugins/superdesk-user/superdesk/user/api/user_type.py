'''
Created on May 27, 2013

@package: superdesk user
@copyright: 2013 Sourcefabric o.p.s.
@license: http://www.gnu.org/licenses/gpl-3.0.txt
@author: Martin Saturka

API specifications for user types.
'''

from ally.api.config import service, model, model
from ally.support.api.keyed import Entity, IEntityService

# --------------------------------------------------------------------

@model
class UserType(Entity):
    '''
    Provides the user type model.
    '''

# --------------------------------------------------------------------
# No query
# --------------------------------------------------------------------

@service((Entity, UserType))
class IUserTypeService(IEntityService):
    '''
    Provides the service methods for the user type.
    '''
