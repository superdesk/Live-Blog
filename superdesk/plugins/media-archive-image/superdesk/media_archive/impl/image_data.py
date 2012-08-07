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
from superdesk.media_archive.core.spec import IMetaDataHandler, IMetaDataReferencer

# --------------------------------------------------------------------

@injected
class ImageDataServiceAlchemy(MetaDataServiceBaseAlchemy, IMetaDataReferencer):
    '''
    @see: IImageDataService
    '''

    handler = IMetaDataHandler

    def __init__(self):
        assert isinstance(self.handler, IMetaDataHandler), \
        'Invalid handler %s' % self.handler
        MetaDataServiceBaseAlchemy.__init__(self, ImageData, QImageData, self)

    # ----------------------------------------------------------------

    def _process(self, metaData, contentPath):
        '''
        @see: MetaDataServiceBaseAlchemy._process
        '''
        return self.handler.process(metaData, contentPath)
    
    # ----------------------------------------------------------------

    def populate(self, metaData, scheme, thumbSize=None):
        #TODO:
        pass
