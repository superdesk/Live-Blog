'''
Created on Apr 19, 2012

@package: superdesk source
@copyright: 2012 Sourcefabric o.p.s.
@license: http://www.gnu.org/licenses/gpl-3.0.txt
@author: Gabriel Nistor

API specifications for source types. A source type provides the understanding (parsing) for content from a source.
'''

from ally.api.config import service
from superdesk.api.domain_superdesk import modelData
from ally.support.api.entity import IEntityGetPrototype, IEntityFindPrototype

# --------------------------------------------------------------------

@modelData(id='Key')
class SourceType:
    '''Provides the source type model.'''
    Key = str
    IsAvailable = bool

# --------------------------------------------------------------------

# No query

# --------------------------------------------------------------------

@service(('Entity', SourceType))
class ISourceTypeService(IEntityGetPrototype, IEntityFindPrototype):
    '''Provides the service methods for the source types.'''
