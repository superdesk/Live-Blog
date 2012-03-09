'''
Created on Mar 6, 2012

@author: Mihai Balaceanu
'''
from superdesk.api import modelSuperDesk
from ally.api.config import service, query
from sql_alchemy.api.entity import Entity, IEntityService, QEntity
from ally.api.criteria import AsLike

# --------------------------------------------------------------------

@modelSuperDesk
class User(Entity):
    '''    
    Provides the user model.
    '''
    Name = str
    
@query
class QUser(QEntity):
    '''
    Query for user service
    '''
    name = AsLike

@service((Entity, User), (QEntity, QUser))
class IUserService(IEntityService):
    '''
    User model service interface
    '''
