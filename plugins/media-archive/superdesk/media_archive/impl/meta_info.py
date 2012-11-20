'''
Created on Apr 19, 2012

@package: superdesk media archive
@copyright: 2012 Sourcefabric o.p.s.
@license: http://www.gnu.org/licenses/gpl-3.0.txt
@author: Gabriel Nistor

SQL Alchemy based implementation for the meta info API. 
'''

from ..api.meta_data import QMetaData
from ..api.meta_info import IMetaInfoService, QMetaInfo
from ..core.impl.meta_service_base import MetaInfoServiceBaseAlchemy
from ..meta.meta_data import MetaDataMapped
from ..meta.meta_info import MetaInfoMapped
from ally.container.ioc import injected
from ally.container.support import setup

# --------------------------------------------------------------------

@injected
@setup(IMetaInfoService)
class MetaInfoServiceAlchemy(MetaInfoServiceBaseAlchemy, IMetaInfoService):
    '''
    Implementation for @see: IMetaInfoService
    '''

    def __init__(self):
        '''
        Construct the meta info service.
        '''
        MetaInfoServiceBaseAlchemy.__init__(self, MetaInfoMapped, QMetaInfo, MetaDataMapped, QMetaData)
