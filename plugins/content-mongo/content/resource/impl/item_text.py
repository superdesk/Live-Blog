'''
Created on Nov 7, 2013

@package: content
@copyright: 2013 Sourcefabric o.p.s.
@license: http://www.gnu.org/licenses/gpl-3.0.txt
@author: Mugur Rus

Implementation for text item.
'''

from ally.api.validate import validate
from ally.container.support import setup
from content.resource.api.item_text import IItemTextService, QItemText
from content.resource.meta.mengine.item_text import ItemTextMapped
from mongo_engine.impl.entity import EntityServiceMongo, EntitySupportMongo

# --------------------------------------------------------------------

@setup(IItemTextService, name='itemTextService')
@validate(ItemTextMapped)
class ItemTextServiceMongo(EntityServiceMongo, IItemTextService):
    '''
    Implementation for @see: IItemTextService
    '''
    
    def __init__(self):
        '''
        Construct the text content item service
        '''
        EntitySupportMongo.__init__(self, ItemTextMapped, QItemText)
