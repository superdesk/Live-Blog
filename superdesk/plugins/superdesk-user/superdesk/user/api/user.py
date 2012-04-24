'''
Created on Mar 6, 2012

@package: superdesk user
@copyright: 2012 Sourcefabric o.p.s.
@license: http://www.gnu.org/licenses/gpl-3.0.txt
@author: Mihai Balaceanu
'''

from ally.api.config import service, query
from ally.api.criteria import AsLikeOrdered
from ally.support.api.entity import Entity, IEntityService, QEntity
from superdesk.api.domain_superdesk import modelSuperDesk
from superdesk.person.api.person import Person, QPerson

# --------------------------------------------------------------------

@modelSuperDesk
class User(Person):
    '''    
    Provides the user model.
    '''
    Name = str

# --------------------------------------------------------------------

@query
class QUser(QPerson):
    '''
    Query for user service
    '''
    name = AsLikeOrdered

# --------------------------------------------------------------------

@service((Entity, User), (QEntity, QUser))
class IUserService(IEntityService):
    '''
    User model service interface
    '''
