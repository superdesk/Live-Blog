'''
Created on Mar 6, 2012

@package: superdesk user
@copyright: 2012 Sourcefabric o.p.s.
@license: http://www.gnu.org/licenses/gpl-3.0.txt
@author: Mihai Balaceanu

The API specifications for the user.
'''

from ally.api.config import service, query, UPDATE, call, LIMIT_DEFAULT
from ally.api.criteria import AsLikeOrdered, AsDateTimeOrdered, AsLike
from ally.support.api.entity import Entity, IEntityService, QEntity
from superdesk.api.domain_superdesk import modelSuperDesk
from superdesk.person.api.person import Person, QPerson
from datetime import datetime
from ally.api.authentication import auth
from ally.api.type import Iter

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
    
    @call
    def getById(self, adminId:auth(User.Id), id:User.Id) -> User:
        '''
        '''       
        
    @call
    def getAll(self, adminId:auth(User.Id), offset:int=None, limit:int=LIMIT_DEFAULT, detailed:bool=True, q:QUser=None) -> Iter(User):
        '''
        '''
    
    @call
    def insert(self, adminId:auth(User.Id), user:User) -> User.Id:
        '''
        '''
        
    @call
    def delete(self, adminId:auth(User.Id), user:User) -> bool:
        '''
        '''
        
    @call
    def update(self, adminId:auth(User.Id), user:User) -> bool:
        '''
        '''
        
    
    @call(method=UPDATE, webName='ChangePassword')
    def changePassword(self, adminId:auth(User.Id), user:UserPassword):
        '''
        Changes user password by user id
        '''
