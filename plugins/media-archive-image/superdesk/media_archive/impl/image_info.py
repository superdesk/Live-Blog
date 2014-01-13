'''
Created on Apr 20, 2012

@package: superdesk media archive
@copyright: 2012 Sourcefabric o.p.s.
@license: http://www.gnu.org/licenses/gpl-3.0.txt
@author: Gabriel Nistor

SQL Alchemy based implementation for the image data API. 
'''

from ally.container.ioc import injected
from ally.container.support import setup
from superdesk.media_archive.core.spec import IQueryIndexer
from ally.container import wire
from superdesk.media_archive.api.image_info import IImageInfoService, QImageInfo
from superdesk.media_archive.core.impl.meta_service_base import MetaInfoServiceBaseAlchemy
from superdesk.media_archive.api.image_data import QImageData, IImageDataService
from superdesk.media_archive.meta.image_data import ImageDataMapped, \
    ImageDataEntry, META_TYPE_KEY
from superdesk.media_archive.meta.image_info import ImageInfoMapped, \
    ImageInfoEntry
from superdesk.media_archive.core.impl.query_service_creator import ISearchProvider


# --------------------------------------------------------------------

@injected
@setup(IImageInfoService, name='imageInfoService')
class ImageInfoServiceAlchemy(MetaInfoServiceBaseAlchemy, IImageInfoService):
    '''
    @see: IImageInfoService
    '''

    queryIndexer = IQueryIndexer;wire.entity('queryIndexer')
    # The query indexer manages the query related information about plugins in order to be able to support the multi-plugin queries
    searchProvider = ISearchProvider; wire.entity('searchProvider')
    # The search provider that will be used to manage all search related activities
    imageDataService = IImageDataService; wire.entity('imageDataService')
    #The correspondent meta data service for image

    def __init__(self):
        assert isinstance(self.queryIndexer, IQueryIndexer), 'Invalid IQueryIndexer %s' % self.queryIndexer
        assert isinstance(self.searchProvider, ISearchProvider), 'Invalid search provider %s' % self.searchProvider
        assert isinstance(self.imageDataService, IImageDataService), 'Invalid image meta data service %s' % self.imageDataService
        
        MetaInfoServiceBaseAlchemy.__init__(self, ImageInfoMapped, QImageInfo, ImageDataMapped, QImageData, 
                                            self.searchProvider, self.imageDataService, META_TYPE_KEY)
        
        self.queryIndexer.register(ImageInfoEntry, QImageInfo, ImageDataEntry, QImageData, META_TYPE_KEY)
        