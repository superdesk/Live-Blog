'''
Created on May 26, 2011

@package: ally api
@copyright: 2012 Sourcefabric o.p.s.
@license: http://www.gnu.org/licenses/gpl-3.0.txt
@author: Gabriel Nistor

General specifications for the entities API that poses an integer Id identifier.
'''

from ally.api.config import model, query, service, call, LIMIT_DEFAULT
from ally.api.type import Iter

# --------------------------------------------------------------------

@model(id='Id')
class Entity:
    '''
    Provides the basic container for an entity that has a Id identifier.
    '''
    Id = int

# --------------------------------------------------------------------

@query(Entity)
class QEntity:
    '''
    Provides the basic query for an entity.
    '''

# --------------------------------------------------------------------

# The Entity model will be replaced by the specific model when the API will be inherited.
@service
class IEntityGetService:
    '''
    Provides the basic entity service. This means locate by id.
    '''

    @call
    def getById(self, id:Entity.Id) -> Entity:
        '''
        Provides the entity based on the id.
        
        @param id: integer
            The id of the entity to find.
        @raise InputError: If the id is not valid. 
        '''

@service
class IEntityFindService:
    '''
    Provides the basic entity find service.
    '''

    @call
    def getAll(self, offset:int=None, limit:int=LIMIT_DEFAULT, detailed:bool=True) -> Iter(Entity):
        '''
        Provides the entities.
        
        @param offset: integer
            The offset to retrieve the entities from.
        @param limit: integer
            The limit of entities to retrieve.
        @param detailed: boolean
            If true will present the total count, limit and offset for the partially returned collection.
        '''

@service
class IEntityQueryService:

    @call
    def getAll(self, offset:int=None, limit:int=LIMIT_DEFAULT, detailed:bool=True, q:QEntity=None) -> Iter(Entity):
        '''
        Provides the entities searched by the provided query.
        
        @param offset: integer
            The offset to retrieve the entities from.
        @param limit: integer
            The limit of entities to retrieve.
        @param detailed: boolean
            If true will present the total count, limit and offset for the partially returned collection.
        @param q: QEntity
            The query to search by.
        '''

@service
class IEntityCRUDService:
    '''
    Provides the entity the CRUD services.
    '''

    @call
    def insert(self, entity:Entity) -> Entity.Id:
        '''
        Insert the entity, also the entity will have automatically assigned the Id to it.
        
        @param entity: Entity
            The entity to be inserted.
        
        @return: The id assigned to the entity
        @raise InputError: If the entity is not valid. 
        '''

    @call
    def update(self, entity:Entity):
        '''
        Update the entity.
        
        @param entity: Entity
            The entity to be updated.
        '''

    @call
    def delete(self, id:Entity.Id) -> bool:
        '''
        Delete the entity for the provided id.
        
        @param id: integer
            The id of the entity to be deleted.
            
        @return: True if the delete is successful, false otherwise.
        '''

@service
class IEntityGetCRUDService(IEntityGetService, IEntityCRUDService):
    '''
    Provides the get and CRUD.
    '''

@service
class IEntityNQService(IEntityGetService, IEntityFindService, IEntityCRUDService):
    '''
    Provides the find without querying, CRUD and query entity services.
    '''

@service
class IEntityService(IEntityGetService, IEntityQueryService, IEntityCRUDService):
    '''
    Provides the find, CRUD and query entity services.
    '''
