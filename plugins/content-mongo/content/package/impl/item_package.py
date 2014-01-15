'''
Created on Dec 13, 2013

@package: content
@copyright: 2013 Sourcefabric o.p.s.
@license: http://www.gnu.org/licenses/gpl-3.0.txt
@author: Mugur Rus

Implementation for content package item.
'''

from ally.api.validate import validate
from ally.container.support import setup
from mongo_engine.impl.entity import EntityServiceMongo, EntitySupportMongo
from content.package.api.item_package import IItemPackageService
from content.package.meta.mengine.item_package import ItemPackageMapped
from content.base.api.item import QItem, IItemService
from content.base.meta.mengine.item import ItemMapped
from ally.container import wire

# --------------------------------------------------------------------

@setup(IItemPackageService, name='itemPackageService')
@validate(ItemPackageMapped)
class ItemPackageServiceMongo(EntityServiceMongo, IItemPackageService):
    '''
    Implementation for @see: IItemPackageService
    '''
    
    itemService = IItemService; wire.entity('itemService')
    
    def __init__(self):
        '''
        Construct the content item service
        '''
        EntitySupportMongo.__init__(self, ItemPackageMapped, QItem)
    
    def getItems(self, packageId):
        '''
        @see: IItemPackageService.getItems
        '''
        assert isinstance(packageId, str), 'Invalid package item identifier %s' % packageId
        package = self.getById(packageId)
        assert isinstance(package, ItemPackageMapped), 'Invalid package item identifier %s' % packageId
        return (item.GUID for item in package.Items)

    def addItem(self, packageId, itemId):
        '''
        @see IItemPackageService.addItem
        '''
        assert isinstance(packageId, str), 'Invalid package item identifier %s' % packageId
        assert isinstance(itemId, str), 'Invalid item identifier %s' % itemId
        package = self.getById(packageId)
        assert isinstance(package, ItemPackageMapped), 'Invalid package item identifier %s' % packageId
        item = self.itemService.getById(itemId)
        assert isinstance(item, ItemMapped), 'Invalid item identifier %s' % itemId
        ItemPackageMapped.objects(GUID=packageId).update_one(push__Items=itemId)

    def removeItem(self, packageId, itemId):
        '''
        @see IItemPackageService.removeItem
        '''
        assert isinstance(packageId, str), 'Invalid package item identifier %s' % packageId
        assert isinstance(itemId, str), 'Invalid item identifier %s' % itemId
        package = self.getById(packageId)
        assert isinstance(package, ItemPackageMapped), 'Invalid package item identifier %s' % packageId
        bool(ItemPackageMapped.objects(GUID=packageId).update_one(pull__Items=itemId))
        return True
