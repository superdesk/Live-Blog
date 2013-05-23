'''
Created on Mar 7, 2013

@package: content packager
@copyright: 2013 Sourcefabric o.p.s.
@license: http://www.gnu.org/licenses/gpl-3.0.txt
@author: Rus Mugurel

API specifications for item.
'''

from content.packager.api.domain_content import modelContent
from datetime import datetime
from ally.api.config import query, service, call, LIMIT_DEFAULT
from ally.api.criteria import AsRangeOrdered, AsLike, AsDateOrdered
from ally.api.type import Iter

# --------------------------------------------------------------------

CLASS_TEXT = 'icls:text'
CLASS_PACKAGE = 'icls:composite'

@modelContent(id='GUId')
class Item:
    '''
    Provides the item model.
    '''
    GUId = str
    Version = int
    ItemClass = str
    Urgency = str
    HeadLine = str
    SlugLine = str
    Byline = str
    CreditLine = str
    FirstCreated = datetime
    VersionCreated = datetime

# --------------------------------------------------------------------

@query(Item)
class QItem:
    '''
    Provides the item query.
    '''
    version = AsRangeOrdered
    itemClass = AsLike
    urgency = AsLike
    headLine = AsLike
    slugLine = AsLike
    byline = AsLike
    creditLine = AsLike
    firstCreated = AsDateOrdered
    versionCreated = AsDateOrdered

# --------------------------------------------------------------------

@service
class IItemService:
    '''
    Provides the service methods for Item model.
    '''

    @call
    def getById(self, guid:Item.GUId) -> Item:
        '''
        Provides the item based on the guid.

        @param guid: string
            The id of the entity to find.
        @raise InputError: If the id is not valid.
        '''

    @call
    def getAll(self, offset:int=None, limit:int=LIMIT_DEFAULT, detailed:bool=True, q:QItem=None) -> Iter(Item):
        '''
        Provides the items searched by the provided query.

        @param offset: integer
            The offset to retrieve the entities from.
        @param limit: integer
            The limit of entities to retrieve.
        @param detailed: boolean
            If true will present the total count, limit and offset for the partially returned collection.
        @param q: QItem
            The query to search by.
        '''

    @call
    def insert(self, item:Item) -> Item.GUId:
        '''
        Insert the item, also the item will have automatically assigned the GUId to it.

        @param item: Item
            The item to be inserted.

        @return: The id assigned to the item
        @raise InputError: If the item is not valid.
        '''

    @call
    def update(self, item:Item):
        '''
        Update the item.

        @param item: Item
            The item to be updated.
        '''

    @call
    def delete(self, id:Item.GUId) -> bool:
        '''
        Delete the item for the provided id.

        @param id: integer
            The id of the item to be deleted.

        @return: True if the delete is successful, false otherwise.
        '''
