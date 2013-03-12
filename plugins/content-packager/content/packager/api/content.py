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

# --------------------------------------------------------------------

@modelContent
class Content(Entity):
    '''
    Provides the content model.
    '''
    ContentType = str
    Content = str
    ResidRef = str
    Href = str
    Size = int
    Rendition = str

# --------------------------------------------------------------------

@query(Content)
class QContent(QEntity):
    '''
    Provides the content query.
    '''
    contentType = AsLike
    size = AsRangeOrdered
    rendition = AsLike

# --------------------------------------------------------------------

@service((Entity, Content))
class IContentService(IEntityService):
    '''
    Provides the service methods for Content model.
    '''
