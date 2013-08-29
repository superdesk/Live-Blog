'''
Created on Mar 8, 2013

@package: content packager
@copyright: 2013 Sourcefabric o.p.s.
@license: http://www.gnu.org/licenses/gpl-3.0.txt
@author: Rus Mugurel

API specifications for content.
'''

from content.packager.api.domain_content import modelContent
from ally.support.api.entity import Entity, QEntity, IEntityService
from ally.api.config import query, service
from ally.api.criteria import AsLike, AsRangeOrdered
from ally.api.type import Reference
from content.packager.api.item import Item

# --------------------------------------------------------------------

@modelContent
class ItemContent(Entity):
    '''
    Provides the item content model.
    '''
    Item = Item
    ContentType = str
    Content = str
    ResidRef = str
    HRef = Reference
    Size = int
    Rendition = str

# --------------------------------------------------------------------

@query(ItemContent)
class QItemContent(QEntity):
    '''
    Provides the item content query.
    '''
    contentType = AsLike
    residRef = AsLike
    size = AsRangeOrdered
    rendition = AsLike

# --------------------------------------------------------------------

@service((Entity, ItemContent), (QEntity, QItemContent))
class IItemContentService(IEntityService):
    '''
    Provides the service methods for ItemContent model.
    '''
