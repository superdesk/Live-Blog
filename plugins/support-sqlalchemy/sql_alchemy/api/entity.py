'''
Created on May 26, 2011

@package Newscoop
@copyright 2011 Sourcefabric o.p.s.
@license http://www.gnu.org/licenses/gpl-3.0.txt
@author: Gabriel Nistor

General specifications for the entities API.
'''

from ally.api.configure import APIModel as model, APIService as service, \
    APIQuery as query, APICall as call
from ally.api.type import Id, Iter
from ally.support.util import Uninstantiable

# --------------------------------------------------------------------

@model()
class Entity:
    '''
    Provides the basic container for an entity that has a primary key.
    '''
    Id = Id

@model()
class Parent(Uninstantiable, Entity):
    '''
    Provides the mark class for parent entities, to not use this in inheritances or otherwise, since this
    class is just intended as a mark model class.
    '''

# --------------------------------------------------------------------

@query()
class QEntity:
    '''
    Provides the basic query for an entity.
    '''
    
# --------------------------------------------------------------------

# The Entity model will be replaced by the specific model when the API will be inherited.
@service()
class IEntityGetService:
    '''
    Provides the basic entity service. This means locate by id.
    '''
    
    @call(Entity, Entity.Id)
    def getById(self, id):
        '''
        Provides the entity based on the id.
        
        @param id: object
            The id of the entity to find.
        @raise InputException: If the id is not valid. 
        '''

@service()
class IEntityFindService:
    '''
    Provides the basic entity find service.
    '''
    
    @call(Iter(Entity), int, int)
    def getAll(self, offset=None, limit=None):
        '''
        Provides the entities.
        
        @param offset: integer
            The offset to retrieve the entities from.
        @param limit: integer
            The limit of entities to retrieve.
        '''

@service()
class IEntityQueryService:
        
    @call(Iter(Entity), int, int, QEntity)
    def getAll(self, offset=None, limit=None, q=None):
        '''
        Provides the entities searched by the provided query.
        
        @param offset: integer
            The offset to retrieve the entities from.
        @param limit: integer
            The limit of entities to retrieve.
        @param q: QEntity
            The query to search by.
        '''

@service()
class IEntityCRUDService:
    '''
    Provides the entity the CRUD services.
    '''
    
    @call(Entity.Id, Entity)
    def insert(self, entity):
        '''
        Insert the entity.
        
        @param entity: Entity
            The entity to be inserted.
        
        @return: The id of the entity
        @raise InputException: If the entity is not valid. 
        '''
        
    @call(None, Entity)
    def update(self, entity):
        '''
        Update the entity.
        
        @param entity: Entity
            The entity to be updated.
        '''
        
    @call(bool, Entity.Id)
    def delete(self, id):
        '''
        Delete the entity for the provided id.
        
        @param id: integer
            The id of the entity to be deleted.
            
        @return: True if the delete is successful, false otherwise.
        '''
        
@service()
class IEntityNQService(IEntityGetService, IEntityFindService, IEntityCRUDService):
    '''
    Provides the find without querying, CRUD and query entity services.
    '''
    
@service()
class IEntityService(IEntityGetService, IEntityQueryService, IEntityCRUDService):
    '''
    Provides the find, CRUD and query entity services.
    '''
