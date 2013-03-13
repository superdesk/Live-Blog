'''
Created on Mar 11, 2013

@package: content packager
@copyright: 2013 Sourcefabric o.p.s.
@license: http://www.gnu.org/licenses/gpl-3.0.txt
@author: Rus Mugurel

API implementation for reference.
'''

from ally.container.support import setup
from content.packager.api.reference import IReferenceService, QReference
from ally.exception import InputError, Ref
from content.packager.meta.reference import ReferenceMapped
from ally.api.extension import IterPart
from ally.support.sqlalchemy.util_service import buildQuery, buildLimits, handle
from ally.api.type import typeFor
from ally.support.api.util_service import copy
from sqlalchemy.exc import SQLAlchemyError, OperationalError
import logging
from ally.support.sqlalchemy.session import SessionSupport

# --------------------------------------------------------------------

log = logging.getLogger(__name__)

# --------------------------------------------------------------------

@setup(IReferenceService, name='referenceService')
class ReferenceServiceAlchemy(SessionSupport, IReferenceService):
    '''
    Implementation for @see: IReferenceService
    '''

    def __init__(self):
        '''
        Construct the reference service.
        '''
        self.Entity = ReferenceMapped
        self.QEntity = QReference
        self.modelType = typeFor(self.Entity)
        self.model = self.modelType.container
        self.queryType = typeFor(QReference)

    def getById(self, idref):
        '''
        Implementation for @see: IReferenceService.getById
        '''
        reference = self.session().query(ReferenceMapped).get(idref)
        if not reference: raise InputError(Ref(_('Unknown id'), ref=ReferenceMapped.Idref))
        return reference

    def getAll(self, offset, limit, detailed, q):
        '''
        Implementation for @see: IReferenceService.getAll
        '''
        if detailed:
            references, total = self._getAllWithCount(None, q, offset, limit)
            return IterPart(references, total, offset, limit)
        return self._getAll(None, q, offset, limit)

    def insert(self, reference):
        '''
        @see: IEntityCRUDService.insert
        '''
        assert self.modelType.isValid(reference), 'Invalid reference %s, expected %s' % (reference, self.Entity)
        referenceDb = copy(reference, self.Entity())
        try:
            self.session().add(referenceDb)
            self.session().flush((referenceDb,))
        except SQLAlchemyError as e: handle(e, referenceDb)
        reference.Idref = referenceDb.Idref
        return referenceDb.Idref

    def update(self, reference):
        '''
        @see: IEntityCRUDService.update
        '''
        assert self.modelType.isValid(reference), 'Invalid reference %s, expected %s' % (reference, self.Entity)
        assert isinstance(reference.Idref, int), 'Invalid reference %s, with id %s' % (reference, reference.Idref)
        referenceDb = self.session().query(self.Entity).get(reference.Idref)
        if not referenceDb: raise InputError(Ref(_('Unknown id'), ref=self.Entity.Idref))
        try: self.session().flush((copy(reference, referenceDb),))
        except SQLAlchemyError as e: handle(e, self.Entity)

    def delete(self, id):
        '''
        @see: IEntityCRUDService.delete
        '''
        try:
            return self.session().query(self.Entity).filter(self.Entity.Idref == id).delete() > 0
        except OperationalError:
            assert log.debug('Could not delete reference %s with id \'%s\'', self.Entity, id, exc_info=True) or True
            raise InputError(Ref(_('Cannot delete because is in use'), model=self.model))

# --------------------------------------------------------------------

    def _getAll(self, filter=None, query=None, offset=None, limit=None, sql=None):
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
        @param sql: SQL alchemy|None
            The sql alchemy query to use.
        @return: list
            The list of all filtered and limited elements.
        '''
        if limit == 0: return []
        sql = sql or self.session().query(self.Entity)
        if filter is not None: sql = sql.filter(filter)
        if query:
            assert self.QEntity, 'No query provided for the entity service'
            assert self.queryType.isValid(query), 'Invalid query %s, expected %s' % (query, self.QEntity)
            sql = buildQuery(sql, query, self.Entity)
        sql = buildLimits(sql, offset, limit)
        return sql.all()

    def _getAllWithCount(self, filter=None, query=None, offset=None, limit=None, sql=None):
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
        @param sql: SQL alchemy|None
            The sql alchemy query to use.
        @return: tuple(list, integer)
            The list of all filtered and limited elements and the count of the total elements.
        '''
        sql = sql or self.session().query(self.Entity)
        if filter is not None: sql = sql.filter(filter)
        if query:
            assert self.QEntity, 'No query provided for the entity service'
            assert self.queryType.isValid(query), 'Invalid query %s, expected %s' % (query, self.QEntity)
            sql = buildQuery(sql, query, self.Entity)
        sqlLimit = buildLimits(sql, offset, limit)
        if limit == 0: return (), sql.count()
        return sqlLimit.all(), sql.count()
