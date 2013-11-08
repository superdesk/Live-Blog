'''
Created on Nov 7, 2013

@package: content
@copyright: 2013 Sourcefabric o.p.s.
@license: http://www.gnu.org/licenses/gpl-3.0.txt
@author: Mugur Rus

API specifications for content item.
'''

import logging
from sql_alchemy.impl.entity import EntityServiceAlchemy
from ally.api.validate import validate
from content.base.api.item import IItemService, QItem
from content.base.meta.item import ItemMapped
from ally.container.support import setup

# --------------------------------------------------------------------

log = logging.getLogger(__name__)

# --------------------------------------------------------------------

@setup(IItemService, name='itemService')
@validate(ItemMapped)
class ItemServiceAlchemy(EntityServiceAlchemy, IItemService):
    '''
    Implementation for @see: IItemService
    '''
    
    def __init__(self):
        EntityServiceAlchemy.__init__(self, ItemMapped, QItem)
