'''
Created on Mar 8, 2013

@package: content packager
@copyright: 2013 Sourcefabric o.p.s.
@license: http://www.gnu.org/licenses/gpl-3.0.txt
@author: Rus Mugurel

API specifications for reference.
'''

from content.packager.api.domain_content import modelContent
from ally.api.config import query, service
from ally.api.criteria import AsLike, AsRangeOrdered, AsEqual
from ally.support.api.entity import Entity, IEntityService, QEntity
from ally.api import type
from content.packager.api.item_group import ItemGroup

# --------------------------------------------------------------------

@modelContent
class Reference(Entity):
    '''
    Provides the reference model.
    '''
    ItemGroup = ItemGroup
    ItemClass = str
    ResidRef = str
    HRef = type.Reference
    Size = int
    Rendition = str
    ContentType = str
    Format = str

# --------------------------------------------------------------------

@query(Reference)
class QReference(QEntity):
    '''
    Provides the reference query.
    '''
    itemGroup = AsEqual
    itemClass = AsLike
    size = AsRangeOrdered
    rendition = AsLike
    contentType = AsLike
    format = AsLike

# --------------------------------------------------------------------

@service((Entity, Reference), (QEntity, QReference))
class IReferenceService(IEntityService):
    '''
    Provides the service methods for Reference model.
    '''
