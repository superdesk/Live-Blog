'''
Created on May 22, 2013

@package: support
@copyright: 2013 Sourcefabric o.p.s.
@license: http://www.gnu.org/licenses/gpl-3.0.txt
@author: Gabriel Nistor

Provides configurations API support that can be binded to other entities.
'''

from ally.api.config import query, service, call, LIMIT_DEFAULT, model
from ally.api.criteria import AsLikeOrdered
from ally.api.type import Iter
from ally.support.api.entity import Entity, QEntity

# --------------------------------------------------------------------

@model(id='Name')
class Configuration:
    '''
    Provides the configuration model.
    '''
    Name = str
    Value = str

# --------------------------------------------------------------------

@query(Configuration)
class QConfiguration(QEntity):
    '''
    Provides the query for the configuration model.
    '''
    name = AsLikeOrdered

# --------------------------------------------------------------------

@service
class IConfigurationService:
    '''
    Provides the configuration service.
    '''
    
    @call
    def getByName(self, parentId:Entity.Id, name:Configuration.Name) -> Configuration:
        '''
        Provides the configuration based on the parentId and name.
        
        @param parentId: integer
            The id of the entity which config is to be used.
        @param name: string
            The name of the configuration property to be taken.
        @raise InputError: If the parentId is not valid. 
        '''

    @call
    def getAll(self, parentId:Entity.Id, offset:int=None, limit:int=LIMIT_DEFAULT, detailed:bool=True,
               q:QConfiguration=None) -> Iter(Configuration):
        '''
        Provides the configuration relating the parentId.
        '''

    @call
    def insert(self, parentId:Entity.Id, configuration:Configuration) -> Configuration.Name:
        '''
        Insert the configuration
        
        @param parentId: integer
            The entity to be configured.
        @param configuration: Configuration
            The configuration to be inserted.
        
        @return: The name of the configuration
        @raise InputError: If the parentId is not valid. 
        '''

    @call
    def update(self, parentId:Entity.Id, configuration:Configuration):
        '''
        Update the configuration on parentId.
        
        @param parentId: integer
            The entity to be configured.
        @param configuration: Configuration
            The configuration to be updated.
        '''

    @call
    def delete(self, parentId:Entity.Id, name:Configuration.Name) -> bool:
        '''
        Delete the configuration on parentId for the provided name.
        
        @param parentId: integer
            The entity to be configured.
        @param name: configuration name
            The configuration to be deleted.
            
        @return: True if the delete is successful, false otherwise.
        '''
