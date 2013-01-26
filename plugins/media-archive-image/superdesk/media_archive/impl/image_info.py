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
from superdesk.media_archive.core.spec import QueryIndexer
from ally.container import wire
from superdesk.media_archive.api.image_info import IImageInfoService, QImageInfo
from superdesk.media_archive.core.impl.meta_service_base import MetaInfoServiceBaseAlchemy
from superdesk.media_archive.api.image_data import QImageData
from superdesk.media_archive.meta.image_data import ImageDataMapped, \
    ImageDataEntry, META_TYPE_KEY
from superdesk.media_archive.meta.image_info import ImageInfoMapped, \
    ImageInfoEntry


# --------------------------------------------------------------------

@injected
@setup(IImageInfoService, name='imageInfoService')
class ImageInfoServiceAlchemy(MetaInfoServiceBaseAlchemy, IImageInfoService):
    '''
    @see: IImageInfoService
    '''

    queryIndexer = QueryIndexer; wire.entity('queryIndexer')

    def __init__(self):
        assert isinstance(self.queryIndexer, QueryIndexer), 'Invalid query indexer %s' % self.queryIndexer
        MetaInfoServiceBaseAlchemy.__init__(self, ImageInfoMapped, QImageInfo, ImageDataMapped, QImageData)
        
        self.queryIndexer.register(ImageInfoEntry, QImageInfo, ImageDataEntry, QImageData, META_TYPE_KEY)
