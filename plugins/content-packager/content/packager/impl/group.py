'''
Created on Mar 11, 2013

@package: content packager
@copyright: 2013 Sourcefabric o.p.s.
@license: http://www.gnu.org/licenses/gpl-3.0.txt
@author: Rus Mugurel

API implementation for group.
'''

from ally.container.support import setup
from sql_alchemy.impl.entity import EntityServiceAlchemy
from content.packager.api.group import IGroupService, IGroupReferenceService, \
    QGroup
from content.packager.meta.group import GroupMapped, GroupReferenceMapped
from ally.api.type import typeFor
from ally.support.sqlalchemy.util_service import buildQuery, buildLimits, handle
from ally.exception import InputError, Ref
from ally.api.extension import IterPart
from ally.support.api.util_service import copy
from sqlalchemy.exc import SQLAlchemyError, OperationalError
import logging

# --------------------------------------------------------------------

log = logging.getLogger(__name__)

# --------------------------------------------------------------------

@setup(IGroupService, name='groupService')
class GroupServiceAlchemy(IGroupService):
    '''
    Implementation for @see: IGroupService
    '''

    def __init__(self):
        '''
        Construct the group service.
        '''
        self.Entity = GroupMapped
        self.QEntity = QGroup
        self.modelType = typeFor(self.Entity)
        self.model = self.modelType.container
        self.queryType = typeFor(QGroup)

    def getById(self, idref):
        '''
        Implementation for @see: IItemService.getById
        '''
        item = self.session().query(GroupMapped).get(idref)
        if not item: raise InputError(Ref(_('Unknown id'), ref=GroupMapped.Id))
        return item

    def getAll(self, offset, limit, detailed, q):
        '''
        Implementation for @see: IItemService.getAll
        '''
        if detailed:
            items, total = self._getAllWithCount(None, q, offset, limit)
            return IterPart(items, total, offset, limit)
        return self._getAll(None, q, offset, limit)

    def insert(self, item):
        '''
        @see: IItemService.insert
        '''
        assert self.modelType.isValid(item), 'Invalid item %s, expected %s' % (item, GroupMapped)
        itemDb = copy(item, GroupMapped())
        assert isinstance(itemDb, GroupMapped)
        try:
            self.session().add(itemDb)
            self.session().flush((itemDb,))
        except SQLAlchemyError as e: handle(e, itemDb)
        item.Id = itemDb.Id
        return itemDb.Id

    def update(self, item):
        '''
        @see: IItemService.update
        '''
        assert self.modelType.isValid(item), 'Invalid item %s, expected %s' % (item, GroupMapped)
        assert isinstance(item.Id, int), 'Invalid item %s, with id %s' % (item, item.Id)
        itemDb = self.session().query(GroupMapped).get(item.Id)
        if not itemDb: raise InputError(Ref(_('Unknown id'), ref=GroupMapped.Id))
        try: self.session().flush((copy(item, itemDb),))
        except SQLAlchemyError as e: handle(e, GroupMapped)

    def delete(self, guid):
        '''
        @see: IItemService.delete
        '''
        try:
            return self.session().query(GroupMapped).filter(GroupMapped.Id == guid).delete() > 0
        except OperationalError:
            assert log.debug('Could not delete item %s with id \'%s\'', GroupMapped, guid, exc_info=True) or True
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
        sql = sql or self.session().query(GroupMapped)
        if filter is not None: sql = sql.filter(filter)
        if query:
            assert self.queryType.isValid(query), 'Invalid query %s, expected %s' % (query, QGroup)
            sql = buildQuery(sql, query, GroupMapped)
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
        sql = sql or self.session().query(GroupMapped)
        if filter is not None: sql = sql.filter(filter)
        if query:
            assert self.queryType.isValid(query), 'Invalid query %s, expected %s' % (query, QGroup)
            sql = buildQuery(sql, query, GroupMapped)
        sqlLimit = buildLimits(sql, offset, limit)
        if limit == 0: return (), sql.count()
        return sqlLimit.all(), sql.count()

# --------------------------------------------------------------------

@setup(IGroupReferenceService, name='groupReferenceService')
class GroupReferenceServiceAlchemy(EntityServiceAlchemy, IGroupReferenceService):
    '''
    Implementation for @see: IGroupReferenceService
    '''

    def __init__(self):
        '''
        Construct the group reference service.
        '''
        EntityServiceAlchemy.__init__(self, GroupReferenceMapped)
