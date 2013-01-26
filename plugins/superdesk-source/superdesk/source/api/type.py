'''
Created on Apr 19, 2012

@package: superdesk source
@copyright: 2012 Sourcefabric o.p.s.
@license: http://www.gnu.org/licenses/gpl-3.0.txt
@author: Gabriel Nistor

API specifications for source types. A source type provides the understanding (parsing) for content from a source.
'''

from ally.api.config import service
from ally.support.api.keyed import Entity, IEntityGetService, IEntityFindService
from superdesk.api.domain_superdesk import modelData

# --------------------------------------------------------------------

@modelData
class SourceType(Entity):
    '''
    Provides the source type model.
    '''
    Name = str
    IsAvailable = bool

# --------------------------------------------------------------------

# No query

# --------------------------------------------------------------------

@service((Entity, SourceType))
class ISourceTypeService(IEntityGetService, IEntityFindService):
    '''
    Provides the service methods for the source types.
    '''
