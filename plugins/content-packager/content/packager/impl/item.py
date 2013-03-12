'''
Created on Mar 11, 2013

@package: content packager
@copyright: 2013 Sourcefabric o.p.s.
@license: http://www.gnu.org/licenses/gpl-3.0.txt
@author: Rus Mugurel

API implementation for item.
'''

from ally.container.support import setup
from content.packager.api.item import IItemService, IItemGroupService, \
    IItemContentService, QItem
from sql_alchemy.impl.entity import EntityServiceAlchemy, EntitySupportAlchemy
from content.packager.meta.item import ItemGroupMapped, ItemContentMapped, \
    ItemMapped
from ally.exception import InputError, Ref
from ally.api.extension import IterPart

# --------------------------------------------------------------------

@setup(IItemService, name='itemService')
class ItemServiceAlchemy(EntitySupportAlchemy, IItemService):
    '''
    Implementation for @see: IItemService
    '''

    def __init__(self):
        '''
        Construct the item service.
        '''
        EntitySupportAlchemy.__init__(self, ItemMapped, QItem)

    def getById(self, idref):
        '''
        Implementation for @see: IItemService.getById
        '''
        item = self.session().query(ItemMapped).get(idref)
        if not item: raise InputError(Ref(_('Unknown id'), ref=ItemMapped.Guid))
        return item

    def getAll(self, offset, limit, detailed, q):
        '''
        Implementation for @see: IItemService.getAll
        '''
        if detailed:
            items, total = self._getAllWithCount(None, q, offset, limit)
            return IterPart(items, total, offset, limit)
        return self._getAll(None, q, offset, limit)

# --------------------------------------------------------------------

@setup(IItemGroupService, name='itemGroupService')
class ItemGroupServiceAlchemy(EntityServiceAlchemy, IItemGroupService):
    '''
    Implementation for @see: IItemGroupService
    '''

    def __init__(self):
        '''
        Construct the item group service.
        '''
        EntityServiceAlchemy.__init__(self, ItemGroupMapped)

# --------------------------------------------------------------------

@setup(IItemContentService, name='itemContentService')
class ContentServiceAlchemy(EntityServiceAlchemy, IItemContentService):
    '''
    Implementation for @see: IItemContentService
    '''

    def __init__(self):
        '''
        Construct the item content service.
        '''
        EntityServiceAlchemy.__init__(self, ItemContentMapped)
