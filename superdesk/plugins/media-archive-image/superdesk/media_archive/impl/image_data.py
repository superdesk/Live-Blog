'''
Created on Apr 19, 2012

@package: superdesk media archive
@copyright: 2012 Sourcefabric o.p.s.
@license: http://www.gnu.org/licenses/gpl-3.0.txt
@author: Gabriel Nistor

SQL Alchemy based implementation for the image data API. 
'''

from ..api.image_data import IImageDataService, QImageData
from ..meta.image_data import ImageData
from .meta_data import MetaDataServiceBaseAlchemy
from ally.container.ioc import injected
from superdesk.media_archive.impl.meta_data import IMetaDataReferenceHandler

# --------------------------------------------------------------------

@injected
class ImageDataServiceAlchemy(MetaDataServiceBaseAlchemy, IImageDataService):
    '''
    @see: IImageDataService
    '''

    referenceHandler = IMetaDataReferenceHandler

    def __init__(self):
        assert isinstance(self.referenceHandler, IMetaDataReferenceHandler), \
        'Invalid reference handler %s' % self.referenceHandler
        MetaDataServiceBaseAlchemy.__init__(self, ImageData, QImageData)

    # ----------------------------------------------------------------

    def _process(self, metaData, scheme, thumbSize):
        '''
        @see: MetaDataServiceBaseAlchemy._process
        '''
        return self.referenceHandler.process(metaData, scheme, thumbSize)
