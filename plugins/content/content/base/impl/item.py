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
from content.base.api.item import QItem, IItemService, Item
from content.base.meta.item import ItemMapped
from ally.container.ioc import injected
from ally.container.support import setup
from ally.container import wire
from content.base.core.spec import IItemHandler
from ally.api import config
from ally.api.type import typeFor
from sql_alchemy.support.util_service import deleteModel

# --------------------------------------------------------------------

log = logging.getLogger(__name__)

# --------------------------------------------------------------------

@setup(name='itemHandlersSetup')
@injected
class ItemHandlersSetup:
    
    itemHandlers = list; wire.entity('itemHandlers')
    # The list of item handlers to delegate to
    
    def __init__(self):
        assert isinstance(self.itemHandlers, list), 'Invalid list of item handlers %s' % self.itemHandlers
        if __debug__:
            for handler in self.itemHandlers:
                assert isinstance(handler, IItemHandler), 'Invalid handler %s' % handler
    
    def createService(self):
        models = set()
        for handler in self.itemHandlers:
            assert isinstance(handler, IItemHandler), 'Invalid handler %s' % handler
            handler.register(models)
        
        topModels = set()
        for model in models:
            topModel = True
            for other in models:
                if issubclass(other, model) and other is not model:
                    topModel = False
                    break
            if topModel: topModels.add(model)
        
        Merged = type('Item$Merged', tuple(topModels), {})
        hints = dict(typeFor(Item).hints)
        hints['name'] = 'Item'
        Merged = config.model(**hints)(Merged)
        
        @config.service((Item, Merged))
        class IItemServiceMerged(IItemService):
            '''
            The item service based on the merged item model. 
            '''
        
        class ItemServiceMergedAlchemy(ItemServiceAlchemy, IItemServiceMerged):
            '''
            Implementation of the merged item service.
            '''
        
        return ItemServiceMergedAlchemy(self.itemHandlers)

# --------------------------------------------------------------------

@validate(ItemMapped)
class ItemServiceAlchemy(EntityServiceAlchemy):
    '''
    Implementation for @see: IItemService
    '''
    
    def __init__(self, itemHandlers):
        '''
        Construct the item service
        '''
        self.itemHandlers = itemHandlers
        EntityServiceAlchemy.__init__(self, ItemMapped, QItem)

    def insert(self, item, content=None):
        '''
        Implement @see IItemService.insert
        '''
        for handler in self.itemHandlers:
            assert isinstance(handler, IItemHandler), 'Invalid handler %s' % handler
            result = handler.insert(item, content)
            if result is not None: return result

    def update(self, item, content=None):
        '''
        Implement @see IItemService.update
        '''
        for handler in self.itemHandlers:
            assert isinstance(handler, IItemHandler), 'Invalid handler %s' % handler
            if handler.update(item, content): return

    def delete(self, item):
        '''
        Implement @see IItemService.update
        '''
        itemObj = self.getById(item)
        for handler in self.itemHandlers:
            assert isinstance(handler, IItemHandler), 'Invalid handler %s' % handler
            handler.delete(itemObj)
        return deleteModel(self.Mapped, item)
