'''
Created on May 22, 2013

@package: support
@copyright: 2013 Sourcefabric o.p.s.
@license: http://www.gnu.org/licenses/gpl-3.0.txt
@author: Gabriel Nistor

Provides configurations API support that can be binded to other entities.
'''

from ally.api.config import query, model, prototype
from ally.api.criteria import AsLikeOrdered
from ally.api.type import Iter
from ally.support.api.entity_named import Entity, QEntity
from ally.api.option import SliceAndTotal # @UnusedImport
import abc # @UnusedImport
from ally.support.api.util_service import modelId

# --------------------------------------------------------------------

@model
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

class IConfigurationPrototype(metaclass=abc.ABCMeta):
    '''
    Provides the configuration service.
    '''

    @prototype
    def getByName(self, targetId:lambda p:p.TARGET, name:Configuration) -> Configuration:
        '''
        Returns the configuration based on the target model id for which configuration is
        implemented and the configuration name.

        @param targetId
            The target model id
        @param name: string
            The name of the configuration property to be taken.
        @raise InputError: If targetId is not valid.
        '''

    @prototype
    def getAll(self, targetId:lambda p:p.TARGET, q:QConfiguration=None, **options:SliceAndTotal) -> Iter(Configuration.Name):
        '''
        Returns a list of configurations for the given target model id.
        '''

    @prototype
    def insert(self, targetId:lambda p:modelId(p.TARGET), configuration:Configuration) -> Configuration.Name:
        '''
        Insert configuration for the given target model id.

        @param targetId
            The target model id for which to insert the configuration.
        @param configuration: Configuration
            The configuration to be inserted.
        @return: The name of the configuration
        @raise InputError: If targetId is not valid.
        '''

    @prototype
    def update(self, targetId:lambda p:modelId(p.TARGET), configuration:Configuration):
        '''
        Update the configuration identified through name for the given target model id.

        @param targetId
            The target model id
        @param configuration: Configuration
            The configuration to be updated.
        '''

    @prototype
    def delete(self, targetId:lambda p:p.TARGET, name:Configuration.Name) -> bool:
        '''
        Delete the configuration identified through name for the given target model id.

        @param targetId
            The target model id
        @param name: configuration name
            The name of the configuration to be deleted.

        @return: True if the delete is successful, false otherwise.
        '''
