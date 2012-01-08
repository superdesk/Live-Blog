'''
Created on Jun 23, 2011

@package Newscoop
@copyright 2011 Sourcefabric o.p.s.
@license http://www.gnu.org/licenses/gpl-3.0.txt
@author: Gabriel Nistor

SQL alchemy implementation for the generic entities API.
'''

from ally import internationalization
from ally.api.configure import modelFor, queryFor
from ally.api.operator import Model, Query
from ally.exception import InputException, Ref
from ally.support.sqlalchemy.helper import buildQuery, buildLimits, handle
from ally.support.sqlalchemy.session import SessionSupport
from inspect import isclass
from sqlalchemy.exc import OperationalError, SQLAlchemyError
import logging

# --------------------------------------------------------------------

log = logging.getLogger(__name__)
_ = internationalization.translator(__name__)

# --------------------------------------------------------------------

class EntitySupportAlchemy(SessionSupport):
    '''
    Provides support generic entity handling.
    '''
    
    def __init__(self, model, query=None, mapper=None):
        if isclass(model): model = modelFor(model)
        if isclass(query): query = queryFor(query)
        assert not model or isinstance(model, Model), 'Invalid model %s' % model
        assert not query or isinstance(query, Query), 'Invalid query %s' % query
        self.model = model
        self.Entity = model.modelClass
        self.EntityMapper = mapper if mapper is not None else model.modelClass
        self.query = query
        SessionSupport.__init__(self)
    
    def _buildGetAll(self, filter=None, offset=None, limit=None, q=None):
        assert self.EntityMapper, 'No model provided for the entity support'
        aq = self.session().query(self.EntityMapper)
        if filter is not None: aq = aq.filter(filter)
        if q:
            assert self.query, 'No query provided for the entity support'
            assert isinstance(q, self.query.queryClass), \
            'Invalid query %s, expected class %s' % (q, self.query.queryClass)
            aq = buildQuery(aq, self.query, q)
        aq = buildLimits(aq, offset, limit)
        return aq.all()
        
# --------------------------------------------------------------------

class EntityGetServiceAlchemy(EntitySupportAlchemy):
    '''
    Generic implementation for @see: IEntityGetService
    '''
    
    def getById(self, id):
        '''
        @see: IEntityGetService.getById
        '''
        entity = self.session().query(self.EntityMapper).get(id)
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
        return self._buildGetAll(None, offset, limit)

class EntityQueryServiceAlchemy(EntitySupportAlchemy):
    '''
    Generic implementation for @see: IEntityQueryService
    '''
        
    def getAll(self, offset=None, limit=None, q=None):
        '''
        @see: IEntityQueryService.getAll
        '''
        return self._buildGetAll(None, offset, limit, q)


class EntityCRUDServiceAlchemy(EntitySupportAlchemy):
    '''
    Generic implementation for @see: IEntityCRUDService
    '''

    def insert(self, entity):
        '''
        @see: IEntityCRUDService.insert
        '''
        assert isinstance(entity, self.Entity), 'Invalid entity %s, expected class %s' % (entity, self.Entity)
        try:
            self.session().add(entity)
            self.session().flush((entity,))
            self.session().expunge(entity)
            # We need to get it out from the session because in case of new updates on the same entity will have
            # not been propagated since the entity is flushed.
        except SQLAlchemyError as e: handle(e, entity)
        return entity.Id

    def update(self, entity):
        '''
        @see: IEntityCRUDService.update
        '''
        assert isinstance(entity, self.Entity), 'Invalid entity %s, expected class %s' % (entity, self.Entity)
        try:
            self.session().merge(entity)
        except SQLAlchemyError as e: handle(e, self.Entity)

    def delete(self, id):
        '''
        @see: IEntityCRUDService.delete
        '''
        try:
            return self.session().query(self.Entity).filter(self.Entity.Id == id).delete() > 0
        except OperationalError:
            raise InputException(_('Cannot delete because is in use', model=self.model))

class EntityNQServiceAlchemy(EntityGetServiceAlchemy, EntityFindServiceAlchemy, EntityCRUDServiceAlchemy):
    '''
    Generic implementation for @see: IEntityService
    '''
    
    def __init__(self, model):
        EntitySupportAlchemy.__init__(self, model)

class EntityServiceAlchemy(EntityGetServiceAlchemy, EntityQueryServiceAlchemy, EntityCRUDServiceAlchemy):
    '''
    Generic implementation for @see: IEntityService
    '''
