'''
Created on Nov 7, 2013

@package: content
@copyright: 2013 Sourcefabric o.p.s.
@license: http://www.gnu.org/licenses/gpl-3.0.txt
@author: Mugur Rus

API specifications for content item.
'''

from ally.api.config import service, query, call
from datetime import datetime
from ally.support.api.entity import IEntityGetPrototype, IEntityQueryPrototype
from ally.api.criteria import AsRangeIntOrdered, AsDateTimeOrdered
from content.base.api.domain_content import modelContent
from ally.api.model import Content

# --------------------------------------------------------------------

@modelContent(id='GUID')
class Item:
    '''
    Provides the item model.
    '''
    GUID = str
    Version = int
    CreatedOn = datetime
    VersionOn = datetime
    Type = str

# --------------------------------------------------------------------

@query(Item)
class QItem:
    '''
    Provides the query for active item model.
    '''
    version = AsRangeIntOrdered
    createdOn = AsDateTimeOrdered
    versionOn = AsDateTimeOrdered

# --------------------------------------------------------------------

@service(('Entity', Item), ('QEntity', QItem))
class IItemService(IEntityGetPrototype, IEntityQueryPrototype):
    '''
    Provides the service methods for items.
    '''
    
    @call
    def insert(self, item:Item, content:Content=None) -> Item.GUID:
        '''
        Insert the item.
        
        @param item: Item
            The item to be inserted.
        @return: object
            The identifier of the item
        '''

    @call
    def update(self, item:Item, content:Content=None):
        '''
        Update the item.
        
        @param item: Item
            The item to be updated.
        '''

    @call
    def delete(self, identifier:Item) -> bool:
        '''
        Delete the item having the given identifier.
        
        @param identifier: object
            The identifier of the item to be deleted.
        @return: boolean
            True if the delete is successful, false otherwise.
        '''
