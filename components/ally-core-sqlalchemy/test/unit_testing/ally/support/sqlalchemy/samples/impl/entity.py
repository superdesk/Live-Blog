'''
Created on Jun 23, 2011

@package: ally core sql alchemy
@copyright: 2012 Sourcefabric o.p.s.
@license: http://www.gnu.org/licenses/gpl-3.0.txt
@author: Gabriel Nistor

SQL alchemy implementation for the generic entities API.
'''

from ally.api.operator.type import TypeModel, TypeQuery
from ally.api.type import typeFor
from ally.exception import InputError, Ref
from ally.internationalization import _
from ally.support.sqlalchemy.mapper import MappedSupport
from ally.support.sqlalchemy.session import SessionSupport
from ally.support.sqlalchemy.util_service import buildQuery, buildLimits, handle
from inspect import isclass
from sqlalchemy.exc import SQLAlchemyError, OperationalError
import logging

# --------------------------------------------------------------------

log = logging.getLogger(__name__)

# --------------------------------------------------------------------

class EntitySupportAlchemy(SessionSupport):
    '''
    Provides support generic entity handling.
    '''

    def __init__(self, Entity, QEntity=None):
        '''
        Construct the entity support for the provided model class and query class.
        
        @param Entity: class
            The mapped entity model class.
        @param QEntity: class|None
            The query mapped class if there is one.
        '''
        assert isclass(Entity), 'Invalid class %s' % Entity
        assert isinstance(Entity, MappedSupport), 'Invalid mapped class %s' % Entity
        self.modelType = typeFor(Entity)
        assert isinstance(self.modelType, TypeModel), 'Invalid model class %s' % Entity

        self.model = self.modelType.container
        self.Entity = Entity

        if QEntity is not None:
            assert isclass(QEntity), 'Invalid class %s' % QEntity
            self.queryType = typeFor(QEntity)
            assert isinstance(self.queryType, TypeQuery), 'Invalid query class %s' % QEntity
            self.query = self.queryType.query
        else:
            self.query = self.queryType = None
        self.QEntity = QEntity

    def _getAll(self, filter=None, query=None, offset=None, limit=None, sqlQuery=None):
        '''
        Provides all the entities for the provided filter, with offset and limit. Also if query is known to the
        service then also a query can be provided.
        
        @param filter: SQL alchemy filtering|None
            The sql alchemy conditions to filter by.
        @param query: query
            The REST query object to provide filtering on.
        @param offset: integer|None
            The offset to fetch elements from.
        @param limit: integer|None
            The limit of elements to get.
        @param sqlQuery: SQL alchemy|None
            The sql alchemy query to use.
        @return: list
            The list of all filtered and limited elements.
        '''
        if limit == 0: return []
        sqlQuery = sqlQuery or self.session().query(self.Entity)
        if filter is not None: sqlQuery = sqlQuery.filter(filter)
        if query:
            assert self.QEntity, 'No query provided for the entity service'
            assert self.queryType.isValid(query), 'Invalid query %s, expected %s' % (query, self.QEntity)
            sqlQuery = buildQuery(sqlQuery, query, self.Entity)
        sqlQuery = buildLimits(sqlQuery, offset, limit)
        return (entity for entity in sqlQuery.all())

    def _getCount(self, filter=None, query=None, sqlQuery=None):
        '''
        Provides the count for the entities of the provided filter. Also if query is known to the service then also a
        query can be provided.
        
        @param filter: SQL alchemy filtering|None
            The sql alchemy conditions to filter by.
        @param query: query
            The REST query object to provide filtering on.
        @param sqlQuery: SQL alchemy|None
            The sql alchemy query to use.
        @return: integer
            The count of the total elements.
        '''
        sqlQuery = sqlQuery or self.session().query(self.Entity)
        if filter is not None: sqlQuery = sqlQuery.filter(filter)
        if query:
            assert self.QEntity, 'No query provided for the entity service'
            assert self.queryType.isValid(query), 'Invalid query %s, expected %s' % (query, self.QEntity)
            sqlQuery = buildQuery(sqlQuery, query, self.Entity)
        return sqlQuery.count()

    def _getAllWithCount(self, filter=None, query=None, offset=None, limit=None, sqlQuery=None):
        '''
        Provides all the entities for the provided filter, with offset and limit and the total count. Also if query is 
        known to the service then also a query can be provided.
        
        @param filter: SQL alchemy filtering|None
            The sql alchemy conditions to filter by.
        @param query: query
            The REST query object to provide filtering on.
        @param offset: integer|None
            The offset to fetch elements from.
        @param limit: integer|None
            The limit of elements to get.
        @param sqlQuery: SQL alchemy|None
            The sql alchemy query to use.
        @return: tuple(list, integer)
            The list of all filtered and limited elements and the count of the total elements.
        '''
        sqlQuery = sqlQuery or self.session().query(self.Entity)
        if filter is not None: sqlQuery = sqlQuery.filter(filter)
        if query:
            assert self.QEntity, 'No query provided for the entity service'
            assert self.queryType.isValid(query), 'Invalid query %s, expected %s' % (query, self.QEntity)
            sqlQuery = buildQuery(sqlQuery, query, self.Entity)
        sql = buildLimits(sqlQuery, offset, limit)
        if limit == 0: return [], sqlQuery.count()
        return (entity for entity in sql.all()), sqlQuery.count()

# --------------------------------------------------------------------

class EntityGetServiceAlchemy(EntitySupportAlchemy):
    '''
    Generic implementation for @see: IEntityGetService
    '''

    def getById(self, id):
        '''
        @see: IEntityGetService.getById
        '''
        entity = self.session().query(self.Entity).get(id)
        if not entity: raise InputError(Ref(_('Unknown id'), ref=self.Entity.Id))
        return entity

class EntityFindServiceAlchemy(EntitySupportAlchemy):
    '''
    Generic implementation for @see: IEntityFindService
    '''

    def getAll(self, offset=None, limit=None):
        '''
        @see: IEntityQueryService.getAll
        '''
        return self._getAll(None, None, offset, limit)

class EntityQueryServiceAlchemy(EntitySupportAlchemy):
    '''
    Generic implementation for @see: IEntityQueryService
    '''

    def getAll(self, offset=None, limit=None, q=None):
        '''
        @see: IEntityQueryService.getAll
        '''
        return self._getAll(None, q, offset, limit)

class EntityCRUDServiceAlchemy(EntitySupportAlchemy):
    '''
    Generic implementation for @see: IEntityCRUDService
    '''

    def insert(self, entity):
        '''
        @see: IEntityCRUDService.insert
        '''
        assert self.modelType.isValid(entity), 'Invalid entity %s, expected %s' % (entity, self.Entity)
        mentity = self.Entity()
        for prop in self.model.properties:
            if getattr(entity.__class__, prop) in entity: setattr(mentity, prop, getattr(entity, prop))
        try:
            self.session().add(mentity)
            self.session().flush((mentity,))
        except SQLAlchemyError as e: handle(e, mentity)
        entity.Id = mentity.Id
        return entity

    def update(self, entity):
        '''
        @see: IEntityCRUDService.update
        '''
        assert self.modelType.isValid(entity), 'Invalid entity %s, expected %s' % (entity, self.Entity)
        entityDb = self.session().query(self.Entity).get(entity.Id)
        if not entityDb: raise InputError(Ref(_('Unknown id'), ref=self.Entity.Id))
        try:
            for prop in self.model.properties:
                if getattr(entity.__class__, prop) in entity: setattr(entityDb, prop, getattr(entity, prop))
            self.session().flush((entityDb,))
        except SQLAlchemyError as e: handle(e, self.Entity)

    def delete(self, id):
        '''
        @see: IEntityCRUDService.delete
        '''
        try:
            return self.session().query(self.Entity).filter(self.Entity.Id == id).delete() > 0
        except OperationalError:
            raise InputError(Ref(_('Cannot delete because is in use'), model=self.model))

class EntityGetCRUDServiceAlchemy(EntityGetServiceAlchemy, EntityCRUDServiceAlchemy):
    '''
    Generic implementation for @see: IEntityGetCRUDService
    '''

class EntityNQServiceAlchemy(EntityGetServiceAlchemy, EntityFindServiceAlchemy, EntityCRUDServiceAlchemy):
    '''
    Generic implementation for @see: IEntityService
    '''

class EntityServiceAlchemy(EntityGetServiceAlchemy, EntityQueryServiceAlchemy, EntityCRUDServiceAlchemy):
    '''
    Generic implementation for @see: IEntityService
    '''

