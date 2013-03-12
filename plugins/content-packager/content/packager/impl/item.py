'''
Created on Mar 11, 2013

@package: content packager
@copyright: 2013 Sourcefabric o.p.s.
@license: http://www.gnu.org/licenses/gpl-3.0.txt
@author: Rus Mugurel

API implementation for item.
'''

from ally.container.support import setup
from content.packager.api.item import IItemService, Item, IItemGroupService, \
    IItemContentService
from sql_alchemy.impl.entity import EntityServiceAlchemy
from content.packager.meta.item import ItemGroupMapped, ItemContentMapped

# --------------------------------------------------------------------

@setup(IItemService, name='itemService')
class ItemServiceAlchemy(IItemService):
    '''
    Implementation for @see: IItemService
    '''

    def getById(self, idref):
        '''
        Implementation for @see: IItemService.getById
        '''
        item = Item()
        return item

    def getAll(self, offset, limit, detailed, q):
        '''
        Implementation for @see: IItemService.getAll
        '''
        return []

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
