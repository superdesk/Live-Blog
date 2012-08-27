'''
Created on Apr 19, 2012

@package: superdesk media archive
@copyright: 2012 Sourcefabric o.p.s.
@license: http://www.gnu.org/licenses/gpl-3.0.txt
@author: Gabriel Nistor

SQL Alchemy based implementation for the image data API. 
'''

from ..api.image_data import QImageData
from ..meta.image_data import ImageDataMapped
from .meta_data import MetaDataServiceBaseAlchemy
from ally.container.ioc import injected
from ally.container.support import setup
from superdesk.media_archive.core.spec import IMetaDataHandler, IMetaDataReferencer
from superdesk.media_archive.api.image_data import IImageDataService

# --------------------------------------------------------------------

@injected
@setup(IImageDataService)
class ImageDataServiceAlchemy(MetaDataServiceBaseAlchemy, IMetaDataReferencer, IImageDataService):
    '''
    @see: IImageDataService
    '''

    handler = IMetaDataHandler

    def __init__(self):
        assert isinstance(self.handler, IMetaDataHandler), 'Invalid handler %s' % self.handler
        MetaDataServiceBaseAlchemy.__init__(self, ImageDataMapped, QImageData, self)

    
    # ----------------------------------------------------------------

    def populate(self, metaData, scheme, thumbSize=None):
        
        return metaData
