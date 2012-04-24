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
from ally.support.api.entity import Entity, IEntityNQService

# --------------------------------------------------------------------

@modelArchive
class MetaType(Entity):
    '''
    Provides the meta types.
    '''
    Key = str # Provides the key that represents the meta type
    Name = str

# --------------------------------------------------------------------

@service((Entity, MetaType))
class IMetaTypeService(IEntityNQService):
    '''
    Provides the meta type services.
    '''
