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
from ally.api.config import service, query
from ally.api.criteria import AsLike
from ally.support.api.entity import IEntityPrototype

# --------------------------------------------------------------------

CONTENT_TYPE_TEXT = 'text'
# The text class (the value of ItemResource.ItemClass for this item)

@modelContent(polymorph={ItemResource.ContentType: CONTENT_TYPE_TEXT})
class ItemText(ItemResource):
    '''
    Provides the text item model.
    '''
    Content = str

# --------------------------------------------------------------------

@query(ItemResource)
class QItemText(QItemResource):
    '''
    Provides the query for active text item model.
    '''
    content = AsLike

# --------------------------------------------------------------------

@service(('Entity', ItemText), ('QEntity', QItemText))
class IItemTextService(IEntityPrototype):
    '''
    Provides the service methods for text items.
    '''
