'''
Created on Apr 19, 2012

@package: superdesk media archive
@copyright: 2012 Sourcefabric o.p.s.
@license: http://www.gnu.org/licenses/gpl-3.0.txt
@author: Gabriel Nistor

SQL Alchemy based implementation for the meta type API. 
'''

from ..api.meta_type import IMetaTypeService
from ally.container.ioc import injected
from ally.container.support import setup
from sql_alchemy.impl.entity import EntityGetServiceAlchemy, \
    EntityFindServiceAlchemy
from superdesk.media_archive.meta.meta_type import MetaTypeMapped

# --------------------------------------------------------------------

@injected
@setup(IMetaTypeService, name='metaTypeService')
class MetaTypeServiceAlchemy(EntityGetServiceAlchemy, EntityFindServiceAlchemy, IMetaTypeService):
    '''Implementation based on SQL alchemy for @see: IMetaTypeService'''

    def __init__(self):
        '''Construct the service.'''
        EntityGetServiceAlchemy.__init__(self, MetaTypeMapped)
        EntityFindServiceAlchemy.__init__(self, MetaTypeMapped)
