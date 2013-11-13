'''
Created on Nov 8, 2013

@package: content
@copyright: 2013 Sourcefabric o.p.s.
@license: http://www.gnu.org/licenses/gpl-3.0.txt
@author: Mugur Rus

API specifications for content resource item.
'''

from ally.api.config import query
from ally.api.criteria import AsLikeOrdered
from content.base.api.domain_content import modelContent
from content.base.api.item import Item
from ally.api.type import Reference

# --------------------------------------------------------------------

TYPE_RESOURCE = 'resource'
# The resource type.(value of Item.Type for this item)

@modelContent
class ItemResource(Item):
    '''
    Provides the text item model.
    '''
    HeadLine = str
    ContentSet = Reference
    Class = str

# --------------------------------------------------------------------

@query(ItemResource)
class QItemResource:
    '''
    Provides the query for active text item model.
    '''
    headLine = AsLikeOrdered
