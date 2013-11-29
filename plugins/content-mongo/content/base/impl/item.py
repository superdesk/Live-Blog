'''
Created on Nov 7, 2013

@package: content
@copyright: 2013 Sourcefabric o.p.s.
@license: http://www.gnu.org/licenses/gpl-3.0.txt
@author: Mugur Rus

API specifications for content item.
'''

import logging

from ally.container.support import setup
from content.base.api.item import IItemService, QItem
from content.base.meta.item_mongo import ItemMapped
from mongo_engine.impl.entity import EntityGetServiceMongo, \
    EntityQueryServiceMongo, EntitySupportMongo


# --------------------------------------------------------------------
log = logging.getLogger(__name__)

# --------------------------------------------------------------------

# TODO: proper mongoengine support
# TODO: "polymorphBy={'Type': 'Resource'}" on model

@setup(IItemService, name='itemService')
class ItemServiceMongo(EntityGetServiceMongo, EntityQueryServiceMongo, IItemService):
    '''
    Implementation for @see: IItemService
    '''
    
    def __init__(self):
        '''
        Construct the item service
        '''
        EntitySupportMongo.__init__(self, ItemMapped, QItem)

#     def getById(self, guid):
#         item = ItemMapped.objects(GUID=guid).first()
#         return item
#         
#     def getAll(self, q=None, **options):
#         return iterateCollection(ItemMapped.objects, ItemMapped.GUID, **options)
