'''
Created on Jun 23, 2011

@package Newscoop
@copyright 2011 Sourcefabric o.p.s.
@license http://www.gnu.org/licenses/gpl-3.0.txt
@author: Gabriel Nistor

SQL alchemy implementation for the generic entities API.
'''

from ally.api.configure import modelFor, queryFor
from ally.api.operator import Model, Query
from ally.exception import InputException, Ref
from ally.internationalization import _
from ally.support.sqlalchemy.session import SessionSupport
from ally.support.sqlalchemy.util_service import buildQuery, buildLimits, handle
from inspect import isclass
from sqlalchemy.exc import OperationalError, SQLAlchemyError
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
        assert isclass(Entity), 'Invalid model mapped class %s' % Entity
        model = modelFor(Entity)
        assert isinstance(model, Model), 'Invalid mapped class %s, has no model' % Entity
        self.model = model
        self.Entity = Entity
        if QEntity:
            assert isclass(QEntity), 'Invalid query mapped class %s' % QEntity
            query = queryFor(QEntity)
            assert isinstance(query, Query), 'Invalid query %s for class %s' % (query, QEntity)
            self.query = query
            self.QEntity = QEntity
        else:
            self.query = None
            self.QEntity = None
        SessionSupport.__init__(self)
    
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
            assert self.query, 'No query provided for the entity support'
            assert isinstance(query, self.query.queryClass), \
            'Invalid query %s, expected class %s' % (query, self.query.queryClass)
            sqlQuery = buildQuery(sqlQuery, query, self.QEntity)
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
            assert self.query, 'No query provided for the entity support'
            assert isinstance(query, self.query.queryClass), \
            'Invalid query %s, expected class %s' % (query, self.query.queryClass)
            sqlQuery = buildQuery(sqlQuery, query, self.QEntity)
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
            assert self.query, 'No query provided for the entity support'
            assert isinstance(query, self.query.queryClass), \
            'Invalid query %s, expected class %s' % (query, self.query.queryClass)
            sqlQuery = buildQuery(sqlQuery, query, self.QEntity)
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
        if not entity: raise InputException(Ref(_('Unknown id'), ref=self.Entity.Id))
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
        assert isinstance(entity, self.model.modelClass), \
        'Invalid entity %s, expected class %s' % (entity, self.model.modelClass)
        dbEntity = self.model.copy(self.Entity(), entity)
        try:
            self.session().add(dbEntity)
            self.session().flush((dbEntity,))
        except SQLAlchemyError as e: handle(e, dbEntity)
        entity.Id = dbEntity.Id
        return dbEntity.Id

    def update(self, entity):
        '''
        @see: IEntityCRUDService.update
        '''
        assert isinstance(entity, self.model.modelClass), \
        'Invalid entity %s, expected class %s' % (entity, self.model.modelClass)
        entityDb = self.session().query(self.Entity).get(entity.Id)
        if not entityDb: raise InputException(Ref(_('Unknown id'), ref=self.Entity.Id))
        try: self.model.copy(entityDb, entity)
        except SQLAlchemyError as e: handle(e, self.Entity)

    def delete(self, id):
        '''
        @see: IEntityCRUDService.delete
        '''
        try:
            return self.session().query(self.Entity).filter(self.Entity.Id == id).delete() > 0
        except OperationalError:
            raise InputException(Ref(_('Cannot delete because is in use'), model=self.model))

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
