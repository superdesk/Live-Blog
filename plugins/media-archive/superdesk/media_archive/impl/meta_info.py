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
from ally.container import wire
from ally.container.ioc import injected
from ally.container.support import setup
from superdesk.media_archive.core.impl.query_service_creator import \
    ISearchProvider
from superdesk.media_archive.core.spec import IQueryIndexer


# --------------------------------------------------------------------

@injected
@setup(IMetaInfoService)
class MetaInfoServiceAlchemy(MetaInfoServiceBaseAlchemy, IMetaInfoService):
    '''
    Implementation for @see: IMetaInfoService
    '''

    queryIndexer = IQueryIndexer;wire.entity('queryIndexer')
    # The query indexer manages the query related information about plugins in order to be able to support the multi-plugin queries
    searchProvider = ISearchProvider; wire.entity('searchProvider')
    # The search provider that will be used to manage all search related activities


    def __init__(self):
        '''
        Construct the meta info service.
        '''
        assert isinstance(self.queryIndexer, IQueryIndexer), 'Invalid IQueryIndexer %s' % self.queryIndexer
        MetaInfoServiceBaseAlchemy.__init__(self, MetaInfoMapped, QMetaInfo, MetaDataMapped, QMetaData, self.searchProvider)

