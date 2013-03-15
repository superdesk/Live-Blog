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
from ally.api.criteria import AsLike, AsRangeOrdered
from ally.support.api.entity import Entity, IEntityService
from ally.api.type import Reference as ReferenceType

# --------------------------------------------------------------------

@modelContent
class Reference(Entity):
    '''
    Provides the reference model.
    '''
    IdRef = str
    ItemClass = str
    ResidRef = str
    HRef = ReferenceType
    Size = int
    Rendition = str
    ContentType = str
    Format = str

# --------------------------------------------------------------------

@query(Reference)
class QReference:
    '''
    Provides the reference query.
    '''
    idRef = AsLike
    itemClass = AsLike
    size = AsRangeOrdered
    rendition = AsLike
    contentType = AsLike
    format = AsLike

# --------------------------------------------------------------------

@service((Entity, Reference))
class IReferenceService(IEntityService):
    '''
    Provides the service methods for Reference model.
    '''
