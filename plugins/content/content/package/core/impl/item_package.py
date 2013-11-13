'''
Created on Nov 13, 2013

@package: content
@copyright: 2013 Sourcefabric o.p.s.
@license: http://www.gnu.org/licenses/gpl-3.0.txt
@author: Mugur Rus

Implementation for package item handler.
'''

from content.base.core.spec import IItemHandler
from sql_alchemy.support.util_service import SessionSupport, insertModel,\
    updateModel
from ally.container.support import setup
from content.package.api.item_package import ItemPackage
from content.package.meta.item_package import TYPE_PACKAGE, ItemPackageMapped
from content.base.api.item import Item

# --------------------------------------------------------------------

@setup(IItemHandler, name='itemPackageHandler')
class ItemPackageHandlerAlchemy(SessionSupport, IItemHandler):
    '''
    Handler for package item processing.
    '''

    def register(self, models):
        '''
        Implementation for @see IItemHandler.register
        '''
        assert isinstance(models, set), 'Invalid models set %s' % models
        models.add(ItemPackage)
    
    def insert(self, item, content=None):
        '''
        Implementation for @see IItemHandler.insert
        '''
        assert isinstance(item, Item), 'Invalid item %s' % item
        if item.Type == TYPE_PACKAGE:
            return insertModel(ItemPackageMapped, item).GUID

    def update(self, item, content=None):
        '''
        Implementation for @see IItemHandler.update
        '''
        assert isinstance(item, Item), 'Invalid item %s' % item
        if item.Type != TYPE_PACKAGE: return False
        updateModel(ItemPackageMapped, item)
        return True

    def delete(self, item):
        '''
        Implementation for @see IItemHandler.delete
        '''
        assert isinstance(item, Item), 'Invalid item %s' % item
        return True
