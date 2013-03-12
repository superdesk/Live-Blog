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
from ally.support.api.entity import Entity, IEntityService
from content.packager.api.group import Group
from content.packager.api.content import Content
from ally.api.type import Iter

# --------------------------------------------------------------------

CLASS_TEXT = 'icls:text'
CLASS_PACKAGE = 'icls:composite'

@modelContent(id='Guid')
class Item:
    '''
    Provides the item model.
    '''
    Guid = str
    Version = int
    ItemClass = str
    Urgency = str
    Headline = str
    Slugline = str
    Byline = str
    Creditline = str
    FirstCreated = datetime
    VersionCreated = datetime

@modelContent
class ItemGroup(Entity):
    '''
    Provides the item group model.
    '''
    Item = Item
    Group = Group

@modelContent
class ItemContent(Entity):
    '''
    Provides the item content model.
    '''
    Item = Item
    Content = Content

# --------------------------------------------------------------------

@query(Item)
class QItem:
    '''
    Provides the item query.
    '''
    version = AsRangeOrdered
    itemClass = AsLike
    urgency = AsLike
    headline = AsLike
    slugline = AsLike
    byline = AsLike
    creditline = AsLike
    firstCreated = AsDateOrdered
    versionCreated = AsDateOrdered

# --------------------------------------------------------------------

@service
class IItemService:
    '''
    Provides the service methods for Item model.
    '''

    @call
    def getById(self, guid:Item.Guid) -> Item:
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

@service((Entity, ItemGroup))
class IItemGroupService(IEntityService):
    '''
    Provides the service methods for ItemGroup model.
    '''

@service((Entity, ItemContent))
class IItemContentService(IEntityService):
    '''
    Provides the service methods for ItemContent model.
    '''
