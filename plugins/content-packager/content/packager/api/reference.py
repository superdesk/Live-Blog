'''
Created on Mar 8, 2013

@package: content packager
@copyright: 2013 Sourcefabric o.p.s.
@license: http://www.gnu.org/licenses/gpl-3.0.txt
@author: Rus Mugurel

API specifications for reference.
'''

from content.packager.api.domain_content import modelContent
from ally.api.config import query
from ally.api.criteria import AsLike, AsRangeOrdered

# --------------------------------------------------------------------

@modelContent(id='Idref')
class Reference:
    '''
    Provides the reference model.
    '''
    Idref = str
    ItemClass = str
    ResidRef = str
    Href = str
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
    itemClass = AsLike
    size = AsRangeOrdered
    rendition = AsLike
    contentType = AsLike
    format = AsLike

# --------------------------------------------------------------------
