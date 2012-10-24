'''
Created on Mar 6, 2012

@package: superdesk user
@copyright: 2012 Sourcefabric o.p.s.
@license: http://www.gnu.org/licenses/gpl-3.0.txt
@author: Mihai Balaceanu

The API specifications for the user.
'''

from ally.api.config import service, query, UPDATE, call
from ally.api.criteria import AsLikeOrdered, AsDateTimeOrdered, AsLike
from ally.support.api.entity import Entity, IEntityService, QEntity
from superdesk.api.domain_superdesk import modelSuperDesk
from superdesk.person.api.person import Person, QPerson
from datetime import datetime
from ally.api.authentication import auth

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

@modelSuperDesk(name=User)
class UserPassword(Entity):
    '''
    Separate model for password actions, just in case
    '''
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
    
    @call(method=UPDATE, webName='ChangePassword')
    def changePassword(self, adminId:auth(User.Id), user:UserPassword):
        '''
        Changes user password by user id
        '''
