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

# --------------------------------------------------------------------

@injected
class ImageDataServiceAlchemy(MetaDataServiceBaseAlchemy, IImageDataService):
    '''
    @see: IImageDataService
    '''

    def __init__(self):
        MetaDataServiceBaseAlchemy.__init__(self, ImageData, QImageData)
