'''
Created on Mar 6, 2012

@package: superdesk user
@copyright: 2012 Sourcefabric o.p.s.
@license: http://www.gnu.org/licenses/gpl-3.0.txt
@author: Mihai Balaceanu

The API specifications for the user.
'''

from ally.api.config import service, query, UPDATE, call, model
from ally.api.criteria import AsLikeOrdered, AsDateTimeOrdered, AsLike, AsBoolean
from ally.support.api.entity_ided import IEntityService, QEntity, Entity
from datetime import datetime
from superdesk.api.domain_superdesk import modelHR
from superdesk.person.api.person import Person, QPerson
from superdesk.user.api.user_type import UserType

# --------------------------------------------------------------------

@model
class User(Person):
    '''    
    Provides the user model.
    '''
    Type = UserType
    Name = str
    CreatedOn = datetime
    Active = bool
    Password = str

@modelHR
class Password:
    '''
    Separate model for changing password actions.
    '''
    OldPassword = str
    NewPassword = str

# --------------------------------------------------------------------

@query(User)
class QUser(QPerson):
    '''
    Query for user service
    '''
    name = AsLikeOrdered
    all = AsLike
    createdOn = AsDateTimeOrdered
    inactive = AsBoolean

# --------------------------------------------------------------------

@service((Entity, User), (QEntity, QUser))
class IUserService(IEntityService):
    '''
    User model service interface
    '''
    
    @call(method=UPDATE)
    def changePassword(self, id:User.Id, password:Password):
        '''
        Changes user password
        '''
