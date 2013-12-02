'''
Created on Nov 7, 2013

@package: content
@copyright: 2013 Sourcefabric o.p.s.
@license: http://www.gnu.org/licenses/gpl-3.0.txt
@author: Mugur Rus

Implementation for content item.
'''

from ally.api.validate import validate
from ally.container.support import setup
from content.base.api.item import IItemService, QItem
from content.base.meta.mengine.item import ItemMapped
from mongo_engine.impl.entity import EntityGetServiceMongo, \
    EntityQueryServiceMongo, EntitySupportMongo


# --------------------------------------------------------------------
@setup(IItemService, name='itemService')
@validate(ItemMapped)
class ItemServiceMongo(EntityGetServiceMongo, EntityQueryServiceMongo, IItemService):
    '''
    Implementation for @see: IItemService
    '''
    
    def __init__(self):
        '''
        Construct the item service
        '''
        EntitySupportMongo.__init__(self, ItemMapped, QItem)
