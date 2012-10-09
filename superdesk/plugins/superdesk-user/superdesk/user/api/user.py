'''
Created on Mar 6, 2012

@package: superdesk user
@copyright: 2012 Sourcefabric o.p.s.
@license: http://www.gnu.org/licenses/gpl-3.0.txt
@author: Mihai Balaceanu

The API specifications for the user.
'''

from ally.api.config import service, query
from ally.api.criteria import AsLikeOrdered, AsDateTimeOrdered, AsLike
from ally.support.api.entity import Entity, IEntityService, QEntity
from superdesk.api.domain_superdesk import modelSuperDesk
from superdesk.person.api.person import Person, QPerson
from datetime import datetime

# --------------------------------------------------------------------

@modelSuperDesk
class User(Person):
    '''    
    Provides the user model.
    '''
    Name = str
    CreatedOn = datetime
    DeletedOn = datetime
    Password = str

# --------------------------------------------------------------------

@query(User)
class QUser(QPerson):
    '''
    Query for user service
    '''
    name = AsLikeOrdered
    all = AsLike
    createdOn = AsDateTimeOrdered

# --------------------------------------------------------------------

@service((Entity, User), (QEntity, QUser))
class IUserService(IEntityService):
    '''
    User model service interface
    '''
