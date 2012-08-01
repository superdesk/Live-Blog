'''
Created on Jun 23, 2011

@package Newscoop
@copyright 2011 Sourcefabric o.p.s.
@license http://www.gnu.org/licenses/gpl-3.0.txt
@author: Gabriel Nistor

SQL alchemy implementation for the generic entities API.
'''

from ally.exception import InputError, Ref
from inspect import isclass
import logging
from ally.api.type import typeFor
from ally.api.operator.type import TypeModel

# --------------------------------------------------------------------

log = logging.getLogger(__name__)

# --------------------------------------------------------------------

class EntitySupport:
    '''
    Provides support generic entity handling.
    '''

    def __init__(self, clazz):
        assert isclass(clazz), 'Invalid class %s' % clazz
        typeModel = typeFor(clazz)
        assert isinstance(typeModel, TypeModel), 'Invalid model class %s' % clazz
        self.model = typeModel.container
        self.Entity = clazz

        self._entityById = {}

# --------------------------------------------------------------------

class EntityGetService(EntitySupport):
    '''
    Generic implementation for @see: IEntityGetService
    '''

    def getById(self, id):
        '''
        @see: IEntityGetService.getById
        '''
        entity = self._entityById.get(id)
        if not entity: raise InputError(Ref('Unknown id', ref=self.Entity.Id))
        return entity

class EntityFindService(EntitySupport):
    '''
    Generic implementation for @see: IEntityFindService
    '''

    def getAll(self, offset=None, limit=None):
        '''
        @see: IEntityQueryService.getAll
        '''
        if not offset: offset = 0
        if not limit: limit = len(self._entityById)
        if offset < 0: offset = 0
        if offset >= len(self._entityById): offset = len(self._entityById) - 1
        if offset + limit > len(self._entityById): limit = len(self._entityById) - offset
        return (entity for _i, entity in zip(range(offset, offset + limit), self._entityById.values()))

class EntityCRUDService(EntitySupport):
    '''
    Generic implementation for @see: IEntityCRUDService
    '''

    def insert(self, entity):
        '''
        @see: IEntityCRUDService.insert
        '''
        assert isinstance(entity, self.Entity), 'Invalid entity %s, expected class %s' % (entity, self.Entity)
        entity.Id = max(self._entityById.keys()) + 1
        self._entityById[entity.Id] = entity
        return entity.Id

    def update(self, entity):
        '''
        @see: IEntityCRUDService.update
        '''
        assert isinstance(entity, self.Entity), 'Invalid entity %s, expected class %s' % (entity, self.Entity)
        self._entityById[entity.Id] = entity

    def delete(self, id):
        '''
        @see: IEntityCRUDService.delete
        '''
        del self._entityById[id]


class EntityService(EntityGetService, EntityFindService, EntityCRUDService):
    '''
    Generic implementation for @see: IEntityService
    '''
