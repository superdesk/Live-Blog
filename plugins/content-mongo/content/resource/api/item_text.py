'''
Created on Nov 11, 2013

@package: content
@copyright: 2013 Sourcefabric o.p.s.
@license: http://www.gnu.org/licenses/gpl-3.0.txt
@author: Mugur Rus

API specifications for content text item.
'''

from content.base.api.domain_content import modelContent
from content.resource.api.item_resource import ItemResource, QItemResource
from ally.api.config import service, call, GET
from ally.support.api.entity import IEntityPrototype
from ally.api.model import Content
from ally.api.type import Reference

# --------------------------------------------------------------------

CONTENT_TYPE_TEXT = 'text'
# The text class (the value of ItemResource.ItemClass for this item)

@modelContent(polymorph={ItemResource.ContentType: CONTENT_TYPE_TEXT})
class ItemText(ItemResource):
    '''
    Provides the text item model.
    '''

@modelContent(id='Content')
class Formatted:
    ''' '''
    Content = Reference

# --------------------------------------------------------------------

# no query

# --------------------------------------------------------------------

@service(('Entity', ItemText), ('QEntity', QItemResource))
class IItemTextService(IEntityPrototype):
    '''
    Provides the service methods for text items.
    '''

    @call(method=GET, webName='AsHTML')
    def asHTML(self, guid:ItemText) -> Formatted:
        '''
        Return the text item content in HTML format.
        
        @param guid: ItemText
            The text item identifier.
        @return: object
            The text item content
        '''

    @call
    def insert(self, item:ItemText, content:Content) -> ItemText.GUID:
        '''
        Insert the text item.
        
        @param item: ItemText
            The text item to be inserted.
        @return: object
            The identifier of the text item
        '''

    @call
    def update(self, item:ItemText, content:Content=None):
        '''
        Update the text item.
        
        @param item: Item
            The text item to be updated.
        '''

    @call
    def delete(self, identifier:ItemText) -> bool:
        '''
        Delete the text item having the given identifier.
        
        @param identifier: object
            The identifier of the text item to be deleted.
        @return: boolean
            True if the delete is successful, false otherwise.
        '''
