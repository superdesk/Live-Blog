'''
Created on Dec 13, 2013

@package: content
@copyright: 2013 Sourcefabric o.p.s.
@license: http://www.gnu.org/licenses/gpl-3.0.txt
@author: Mugur Rus

API specifications for content package item.
'''

from ally.api.config import service, call, UPDATE
from content.base.api.domain_content import modelContent
from content.base.api.item import Item, QItem
from ally.support.api.entity import IEntityPrototype
from ally.api.type import Iter

# --------------------------------------------------------------------

TYPE_PACKAGE = 'package'
# The package type.(value of Item.Type for this item)

@modelContent(polymorph={Item.Type: TYPE_PACKAGE})
class ItemPackage(Item):
    '''
    Provides the package item model.
    '''

# --------------------------------------------------------------------

@service(('Entity', ItemPackage), ('QEntity', QItem))
class IItemPackageService(IEntityPrototype):
    '''
    Provides the service methods for pacakge items.
    '''

    @call(webName='Sub')
    def getItems(self, packageId:ItemPackage.GUID) -> Iter(Item.GUID):
        '''
        Return the list of items for a package.

        @param packageId: ItemPackage.GUID
            The package item identifier
        @param Item: Item.GUID
            The identifier of the item to be removed.
        @return: Iter(Item)
            Return an iterator over the list of items.
        '''

    @call(method=UPDATE, webName='Sub')
    def addItem(self, packageId:ItemPackage.GUID, itemId:Item.GUID):
        '''
        Add an item to the list of items referenced by this package.

        @param packageId: ItemPackage.GUID
            The package item identifier
        @param Item: Item.GUID
            The identifier of the item to be removed.
        '''

    @call(webName='Sub')
    def removeItem(self, packageId:ItemPackage.GUID, itemId:Item.GUID) -> bool:
        '''
        Remove an item from the list of items referenced by this package.
        
        @param packageId: ItemPackage.GUID
            The package item identifier
        @param Item: Item.GUID
            The identifier of the item to be removed.
        @return: bool
            Return True if the item existed in the references list and was deleted,
            False otherwise.
        '''
