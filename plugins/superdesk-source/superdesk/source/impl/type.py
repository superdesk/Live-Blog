'''
Created on May 3, 2012

@package: superdesk source
@copyright: 2012 Sourcefabric o.p.s.
@license: http://www.gnu.org/licenses/gpl-3.0.txt
@author: Gabriel Nistor

Contains the SQL alchemy implementation for source type API.
'''

from ..api.type import ISourceTypeService
from ally.container.ioc import injected
from ally.container.support import setup
from sql_alchemy.impl.entity import EntityGetServiceAlchemy, EntityFindServiceAlchemy
from superdesk.source.meta.type import SourceTypeMapped

# --------------------------------------------------------------------

@injected
@setup(ISourceTypeService, name='sourceTypeService')
class SourceTypeServiceAlchemy(EntityGetServiceAlchemy, EntityFindServiceAlchemy, ISourceTypeService):
    '''Implementation for @see: ISourceTypeService'''

    def __init__(self):
        '''Construct the source type service.'''
        EntityGetServiceAlchemy.__init__(self, SourceTypeMapped)
        EntityFindServiceAlchemy.__init__(self, SourceTypeMapped)
