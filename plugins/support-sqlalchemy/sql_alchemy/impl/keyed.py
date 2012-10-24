'''
Created on May 2, 2012

@package: support plugin
@copyright: 2012 Sourcefabric o.p.s.
@license: http://www.gnu.org/licenses/gpl-3.0.txt
@author: Gabriel Nistor

SQL alchemy implementation for the generic keyed entities API.
'''

from ally.api.operator.type import TypeModel, TypeQuery
from ally.api.type import typeFor
from ally.exception import InputError, Ref
from ally.internationalization import _
from ally.support.api import keyed as api
from ally.support.api.util_service import copy
from ally.support.sqlalchemy.session import SessionSupport
from ally.support.sqlalchemy.util_service import buildQuery, buildLimits, handle
from inspect import isclass
from sqlalchemy.exc import SQLAlchemyError, OperationalError
from sqlalchemy.orm.exc import NoResultFound
import logging
from ally.support.sqlalchemy.mapper import MappedSupport

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
        assert issubclass(Entity, api.Entity), 'Invalid entity class %s' % Entity
        assert isinstance(Entity, MappedSupport), 'Invalid mapped class %s' % Entity
        self.modelType = typeFor(Entity)
        assert isinstance(self.modelType, TypeModel), 'Invalid model class %s' % Entity

        self.model = self.modelType.container
        self.Entity = Entity

        if QEntity is not None:
            assert isclass(QEntity), 'Invalid class %s' % QEntity
            assert issubclass(QEntity, api.QEntity), 'Invalid query entity class %s' % QEntity
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
        return sqlQuery.all()

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
        return sql.all(), sqlQuery.count()

# --------------------------------------------------------------------

class EntityGetServiceAlchemy(EntitySupportAlchemy):
    '''
    Generic implementation for @see: IEntityGetService
    '''

    def getByKey(self, key):
        '''
        @see: IEntityGetService.getByKey
        '''
        try: return self.session().query(self.Entity).filter(self.Entity.Key == key).one()
        except NoResultFound: raise InputError(Ref(_('Unknown key'), ref=self.Entity.Key))

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
        entityDb = copy(entity, self.Entity())
        try:
            self.session().add(entityDb)
            self.session().flush((entityDb,))
        except SQLAlchemyError as e: handle(e, entityDb)
        return entity.Key

    def update(self, entity):
        '''
        @see: IEntityCRUDService.update
        '''
        assert self.modelType.isValid(entity), 'Invalid entity %s, expected %s' % (entity, self.Entity)
        assert isinstance(entity.Key, str), 'Invalid entity %s, with key %s' % (entity, entity.Key)

        try: entityDb = self.session().query(self.Entity).filter(self.Entity.Key == entity.Key)
        except NoResultFound: raise InputError(Ref(_('Unknown key'), ref=self.Entity.Key))
        try:
            self.session().flush((copy(entity, entityDb),))
        except SQLAlchemyError as e: handle(e, self.Entity)

    def delete(self, key):
        '''
        @see: IEntityCRUDService.delete
        '''
        try:
            return self.session().query(self.Entity).filter(self.Entity.Key == key).delete() > 0
        except OperationalError:
            assert log.debug('Could not delete entity %s with key \'%s\'', self.Entity, key, exc_info=True) or True
            raise InputError(Ref(_('Cannot delete because is in use'), model=self.model))

class EntityGetCRUDServiceAlchemy(EntityGetServiceAlchemy, EntityCRUDServiceAlchemy):
    '''
    Generic implementation for @see: IEntityGetCRUDService
    '''

class EntityNQServiceAlchemy(EntityGetServiceAlchemy, EntityFindServiceAlchemy, EntityCRUDServiceAlchemy):
    '''
    Generic implementation for @see: IEntityService
    '''

    def __init__(self, Entity):
        '''
        @see: EntitySupportAlchemy.__init__
        '''
        EntitySupportAlchemy.__init__(self, Entity)

class EntityServiceAlchemy(EntityGetServiceAlchemy, EntityQueryServiceAlchemy, EntityCRUDServiceAlchemy):
    '''
    Generic implementation for @see: IEntityService
    '''

