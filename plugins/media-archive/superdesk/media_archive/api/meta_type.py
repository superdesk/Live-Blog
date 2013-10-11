'''
Created on Apr 19, 2012

@package: superdesk media archive
@copyright: 2012 Sourcefabric o.p.s.
@license: http://www.gnu.org/licenses/gpl-3.0.txt
@author: Gabriel Nistor

API specifications for meta type.
'''

from .domain_archive import modelArchive
from ally.api.config import service
from ally.api.option import SliceAndTotal # @UnusedImport
from ally.support.api.entity_ided import IEntityFindService, IEntityGetService, \
    Entity

# --------------------------------------------------------------------

@modelArchive
class MetaType(Entity):
    '''Provides the meta types.'''
    Type = str

# --------------------------------------------------------------------

@service((Entity, MetaType))
class IMetaTypeService(IEntityGetService, IEntityFindService):
    '''Provides the meta type services.'''

