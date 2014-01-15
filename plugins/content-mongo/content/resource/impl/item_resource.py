'''
Created on Nov 7, 2013

@package: content
@copyright: 2013 Sourcefabric o.p.s.
@license: http://www.gnu.org/licenses/gpl-3.0.txt
@author: Mugur Rus

Implementation for resource item.
'''

from ally.api.validate import validate
from ally.container.support import setup
from content.resource.api.item_resource import IItemResourceService, \
    QItemResource
from content.resource.meta.mengine.item_resource import ItemResourceMapped
from mongo_engine.impl.entity import EntityServiceMongo, EntitySupportMongo

# --------------------------------------------------------------------

@setup(IItemResourceService, name='itemResourceService')
@validate(ItemResourceMapped)
class ItemResourceServiceMongo(EntityServiceMongo, IItemResourceService):
    '''
    Implementation for @see: IItemResourceService
    '''
    
    def __init__(self):
        '''
        Construct the content item service
        '''
        EntitySupportMongo.__init__(self, ItemResourceMapped, QItemResource)
