'''
Created on Nov 8, 2013

@package: content
@copyright: 2013 Sourcefabric o.p.s.
@license: http://www.gnu.org/licenses/gpl-3.0.txt
@author: Mugur Rus

API specifications for content resource item.
'''

from ally.api.config import query, service
from ally.api.criteria import AsLikeOrdered
from ally.api.type import Reference
from ally.support.api.entity import IEntityPrototype
from content.base.api.domain_content import modelContent
from content.base.api.item import Item, QItem

# --------------------------------------------------------------------

TYPE_RESOURCE = 'resource'
# The resource type.(value of Item.Type for this item)

@modelContent(polymorph={Item.Type: TYPE_RESOURCE})
class ItemResource(Item):
    '''
    Provides the resource item model.
    '''
    ContentType = str
    HeadLine = str
    ContentSet = Reference

# --------------------------------------------------------------------

@query(ItemResource)
class QItemResource(QItem):
    '''
    Provides the query for active text item model.
    '''
    contentType = AsLikeOrdered
    headLine = AsLikeOrdered

# --------------------------------------------------------------------

@service(('Entity', ItemResource), ('QEntity', QItemResource))
class IItemResourceService(IEntityPrototype):
    '''
    Provides the service methods for resource items.
    '''
