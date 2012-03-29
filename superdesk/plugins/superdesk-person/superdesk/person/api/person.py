'''
Created on Mar 6, 2012

@author: Mihai Balaceanu
'''
from superdesk.api import modelSuperDesk
from ally.api.config import service, query, call
from sql_alchemy.api.entity import Entity, IEntityService, QEntity
from ally.api.criteria import AsLike
from superdesk.user.api.user import User
from ally.api.type import Iter

# --------------------------------------------------------------------

@modelSuperDesk
class Person(Entity):
    '''    
    Provides the person model.
    '''
    User = User.Id
    FirstName = str
    LastName = str
    Address = str
    
@query
class QPerson(QEntity):
    '''
    Query for person service
    '''
    name = AsLike

@service((Entity, Person), (QEntity, QPerson))
class IPersonService(IEntityService):
    '''
    Person model service interface
    '''
    @call
    def getByUser(self, idUser:User.Id) -> Iter(Person):
        '''
        Select person by user id
        '''
