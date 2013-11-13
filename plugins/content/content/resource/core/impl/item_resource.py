'''
Created on Nov 13, 2013

@package: content
@copyright: 2013 Sourcefabric o.p.s.
@license: http://www.gnu.org/licenses/gpl-3.0.txt
@author: Mugur Rus

Implementation for resource item handler.
'''

from content.base.core.spec import IItemHandler
from content.resource.api.item_resource import ItemResource, TYPE_RESOURCE
from sql_alchemy.support.util_service import SessionSupport, insertModel,\
    updateModel
from ally.container.support import setup
from content.base.api.item import Item
from content.resource.meta.item_resource import ItemResourceMapped

# --------------------------------------------------------------------

@setup(IItemHandler, name='itemResourceHandler')
class ItemResourceHandlerAlchemy(SessionSupport, IItemHandler):
    '''
    Handler for resource item processing.
    '''

    def register(self, models):
        '''
        Implementation for @see IItemHandler.register
        '''
        assert isinstance(models, set), 'Invalid models set %s' % models
        models.add(ItemResource)

    def insert(self, item, content=None):
        '''
        Implementation for @see IItemHandler.insert
        '''
        assert isinstance(item, Item), 'Invalid item %s' % item
        if item.Type == TYPE_RESOURCE:
            return insertModel(ItemResourceMapped, item).GUID

    def update(self, item, content=None):
        '''
        Implementation for @see IItemHandler.update
        '''
        assert isinstance(item, Item), 'Invalid item %s' % item
        if item.Type != TYPE_RESOURCE: return False
        updateModel(ItemResourceMapped, item)
        return True

    def delete(self, item):
        '''
        Implementation for @see IItemHandler.delete
        '''
        assert isinstance(item, Item), 'Invalid item %s' % item
        if item.Type == TYPE_RESOURCE:
            #TODO::remove file from CDM
            pass
        return True
