'''
Created on May 22, 2013

@package: support
@copyright: 2013 Sourcefabric o.p.s.
@license: http://www.gnu.org/licenses/gpl-3.0.txt
@author: Gabriel Nistor

Provides configurations API support that can be binded to other entities.
'''

from ally.api.config import query, service, call, model
from ally.api.criteria import AsLikeOrdered
from ally.api.type import Iter
from ally.support.api.entity_named import Entity, QEntity
from ally.api.option import SliceAndTotal # @UnusedImport

# --------------------------------------------------------------------

@model(id='Name')
class Configuration(Entity):
    '''
    Provides the configuration model.
    '''
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
    def getByName(self, parentId:Entity.Name, name:Configuration.Name) -> Configuration:
        '''
        Provides the configuration based on the parentId and name.
        
        @param parentId: integer
            The id of the entity which config is to be used.
        @param name: string
            The name of the configuration property to be taken.
        @raise InputError: If the parentId is not valid. 
        '''

    @call
    def getAll(self, parentId:Entity.Name, q:QConfiguration=None, **options:SliceAndTotal) -> Iter(Configuration.Name):
        '''
        Provides the configuration relating the parentId.
        '''

    @call
    def insert(self, parentId:Entity.Name, configuration:Configuration) -> Configuration.Name:
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
    def update(self, parentId:Entity.Name, configuration:Configuration):
        '''
        Update the configuration on parentId.
        
        @param parentId: integer
            The entity to be configured.
        @param configuration: Configuration
            The configuration to be updated.
        '''

    @call
    def delete(self, parentId:Entity.Name, name:Configuration.Name) -> bool:
        '''
        Delete the configuration on parentId for the provided name.
        
        @param parentId: integer
            The entity to be configured.
        @param name: configuration name
            The configuration to be deleted.
            
        @return: True if the delete is successful, false otherwise.
        '''
