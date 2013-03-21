'''
Created on Mar 11, 2013

@package: content packager
@copyright: 2013 Sourcefabric o.p.s.
@license: http://www.gnu.org/licenses/gpl-3.0.txt
@author: Rus Mugurel

API implementation for item.
'''

from ally.container.support import setup
from content.packager.api.item import IItemService, QItem, Item, CLASS_TEXT, \
    CLASS_PACKAGE
from content.packager.meta.item import ItemMapped
from ally.exception import InputError, Ref
from ally.api.extension import IterPart
from ally.support.sqlalchemy.util_service import buildQuery, buildLimits, handle
from ally.support.api.util_service import copy
from sqlalchemy.exc import SQLAlchemyError, OperationalError
import logging
from ally.api.type import typeFor
from ally.support.sqlalchemy.session import SessionSupport
from sqlalchemy.sql.functions import current_timestamp
from ally.container.ioc import injected
from ally.container import wire
from datetime import date
from ally.internationalization import _

# --------------------------------------------------------------------

log = logging.getLogger(__name__)

# --------------------------------------------------------------------

@injected
@setup(IItemService, name='itemService')
class ItemServiceAlchemy(SessionSupport, IItemService):
    '''
    Implementation for @see: IItemService
    '''
    guid_prefix = 'urn:newsml'; wire.config('guid_prefix', doc='''
    The prefix to use in GUId generation''')
    guid_provider = 'default'; wire.config('guid_provider', doc='''
    The provider to use in GUId generation''')
    guid_scheme = '%(prefix)s:%(provider)s:%(dateId)s:%(itemId)s'
    wire.config('guid_scheme', doc='''The prefix to use in GUId generation''')

    def __init__(self):
        '''
        Construct the item service.
        '''
        self.Entity = ItemMapped
        self.QEntity = QItem
        self.modelType = typeFor(self.Entity)
        self.model = self.modelType.container
        self.queryType = typeFor(QItem)

    def getById(self, guid):
        '''
        Implementation for @see: IItemService.getById
        '''
        item = self.session().query(ItemMapped).get(guid)
        if not item: raise InputError(Ref(_('Unknown id'), ref=ItemMapped.GUId))
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
        assert self.modelType.isValid(item), 'Invalid item %s, expected %s' % (item, ItemMapped)
        assert isinstance(item, Item)
        assert item.ItemClass == CLASS_TEXT or item.ItemClass == CLASS_PACKAGE, \
            'Invalid item class %s, expected %s or %s' % (item.ItemClass, CLASS_TEXT, CLASS_PACKAGE)
        itemDb = copy(item, ItemMapped())
        assert isinstance(itemDb, ItemMapped)

        # TODO: generate proper guid: generate better itemId, externalise as a service
        itemDb.GUId = self.guid_scheme % {'prefix':self.guid_prefix, 'provider':self.guid_provider,
                                          'dateId':date.today().strftime('%Y%m%d'), 'itemId':itemDb.SlugLine}
        itemDb.FirstCreated = current_timestamp()
        try:
            self.session().add(itemDb)
            self.session().flush((itemDb,))
        except SQLAlchemyError as e: handle(e, itemDb)
        item.GUId = itemDb.GUId
        return itemDb.GUId

    def update(self, item):
        '''
        @see: IItemService.update
        '''
        assert self.modelType.isValid(item), 'Invalid item %s, expected %s' % (item, ItemMapped)
        assert isinstance(item.GUId, str), 'Invalid item %s, with id %s' % (item, item.GUId)

        itemDb = self.session().query(ItemMapped).get(item.GUId)
        if not itemDb: raise InputError(Ref(_('Unknown id'), ref=ItemMapped.GUId))
        try: self.session().flush((copy(item, itemDb),))
        except SQLAlchemyError as e: handle(e, ItemMapped)

    def delete(self, guid):
        '''
        @see: IItemService.delete
        '''
        try:
            return self.session().query(ItemMapped).filter(ItemMapped.GUId == guid).delete() > 0
        except OperationalError:
            assert log.debug('Could not delete item %s with id \'%s\'', ItemMapped, guid, exc_info=True) or True
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
        sql = sql or self.session().query(ItemMapped)
        if filter is not None: sql = sql.filter(filter)
        if query:
            assert self.queryType.isValid(query), 'Invalid query %s, expected %s' % (query, QItem)
            sql = buildQuery(sql, query, ItemMapped)
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
        sql = sql or self.session().query(ItemMapped)
        if filter is not None: sql = sql.filter(filter)
        if query:
            assert self.queryType.isValid(query), 'Invalid query %s, expected %s' % (query, QItem)
            sql = buildQuery(sql, query, ItemMapped)
        sqlLimit = buildLimits(sql, offset, limit)
        if limit == 0: return (), sql.count()
        return sqlLimit.all(), sql.count()
