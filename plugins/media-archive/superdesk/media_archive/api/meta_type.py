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
from ally.support.api.entity import IEntityGetPrototype, IEntityFindPrototype

# --------------------------------------------------------------------

@modelArchive(id='Type')
class MetaType:
    '''Provides the meta types.'''
    Type = str

# --------------------------------------------------------------------

@service(('Entity', MetaType))
class IMetaTypeService(IEntityGetPrototype, IEntityFindPrototype):
    '''Provides the meta type services.'''

