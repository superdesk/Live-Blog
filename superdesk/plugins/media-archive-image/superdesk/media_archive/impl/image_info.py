'''
Created on Apr 20, 2012

@package: superdesk media archive
@copyright: 2012 Sourcefabric o.p.s.
@license: http://www.gnu.org/licenses/gpl-3.0.txt
@author: Gabriel Nistor

SQL Alchemy based implementation for the image data API. 
'''

from ..api.image_data import QImageData
from ..api.image_info import IImageInfoService, QImageInfo
from ..meta.image_data import ImageDataMapped
from ..meta.image_info import ImageInfoMapped
from .meta_info import MetaInfoServiceBaseAlchemy
from ally.container.ioc import injected

# --------------------------------------------------------------------

@injected
class ImageInfoServiceAlchemy(MetaInfoServiceBaseAlchemy, IImageInfoService):
    '''
    @see: IImageInfoService
    '''

    def __init__(self):
        MetaInfoServiceBaseAlchemy.__init__(self, ImageInfoMapped, QImageInfo, ImageDataMapped, QImageData)
        