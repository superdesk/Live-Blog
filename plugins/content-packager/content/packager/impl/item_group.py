'''
Created on Mar 11, 2013

@package: content packager
@copyright: 2013 Sourcefabric o.p.s.
@license: http://www.gnu.org/licenses/gpl-3.0.txt
@author: Rus Mugurel

API implementation for item group.
'''

from ally.container.support import setup
from ally.api.extension import IterPart
import logging
from content.packager.api.item_group import IItemGroupService, QItemGroup
from content.packager.meta.item_group import ItemGroupMapped
from sql_alchemy.impl.entity import EntityServiceAlchemy

# --------------------------------------------------------------------

log = logging.getLogger(__name__)

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
        EntityServiceAlchemy.__init__(self, ItemGroupMapped, QItemGroup)

    def getItemGroups(self, item, offset, limit, detailed, q):
        '''
        Implementation for @see: IItemService.getItemGroups
        '''
        assert isinstance(q, QItemGroup)
        q.item = item
        if detailed:
            groups, total = self._getAllWithCount(None, q, offset, limit)
            return IterPart(groups, total, offset, limit)
        return self._getAll(None, q, offset, limit)
