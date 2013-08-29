'''
Created on Mar 8, 2013

@package: content packager
@copyright: 2013 Sourcefabric o.p.s.
@license: http://www.gnu.org/licenses/gpl-3.0.txt
@author: Rus Mugurel

API specifications for item group.
'''

from content.packager.api.domain_content import modelContent
from ally.api.config import query, service, call, LIMIT_DEFAULT
from ally.api.criteria import AsLike
from ally.api.type import Iter
from content.packager.api.item import Item
from ally.support.api.entity import Entity, IEntityService, QEntity

# --------------------------------------------------------------------

@modelContent
class ItemGroup(Entity):
    '''
    Provides the item group model.
    '''
    Item = Item
    LocalId = str
    Role = str
    Mode = str

# --------------------------------------------------------------------

@query(ItemGroup)
class QItemGroup(QEntity):
    '''
    Provides the item group query.
    '''
    localId = AsLike
    role = AsLike
    mode = AsLike

# --------------------------------------------------------------------

@service((Entity, ItemGroup), (QEntity, QItemGroup))
class IItemGroupService(IEntityService):
    '''
    Provides the service methods for item group.
    '''

    @call
    def getItemGroups(self, item:Item.GUId, offset:int=None, limit:int=LIMIT_DEFAULT, detailed:bool=True, q:QItemGroup=None) -> Iter(ItemGroup):
        '''
        Provides the item groups for the given item and searched by the provided query.

        @param item: Item.GUId
            The item identifier
        @param offset: integer
            The offset to retrieve the item groups from.
        @param limit: integer
            The limit of item groups to retrieve.
        @param detailed: boolean
            If true will present the total count, limit and offset for the partially returned collection.
        @param q: QItemGroup
            The query to search by.
        '''
