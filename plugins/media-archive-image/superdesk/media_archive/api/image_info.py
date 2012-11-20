'''
Created on Apr 19, 2012

@package: superdesk media archive
@copyright: 2012 Sourcefabric o.p.s.
@license: http://www.gnu.org/licenses/gpl-3.0.txt
@author: Gabriel Nistor

API specifications for media archive image info.
'''

from .domain_archive import modelArchive
from .image_data import ImageData, QImageData
from .meta_data import MetaData, QMetaData
from .meta_info import MetaInfo, QMetaInfo, IMetaInfoService
from ally.api.config import query, service
from ally.api.criteria import AsLikeOrdered

# --------------------------------------------------------------------

@modelArchive
class ImageInfo(MetaInfo):
    '''
    Provides the meta info image.
    '''
    MetaData = ImageData
    Caption = str

# --------------------------------------------------------------------

@query(ImageInfo)
class QImageInfo(QMetaInfo):
    '''
    The query for image info model.
    '''
    caption = AsLikeOrdered

# --------------------------------------------------------------------

@service((MetaInfo, ImageInfo), (QMetaInfo, QImageInfo), (MetaData, ImageData), (QMetaData, QImageData))
class IImageInfoService(IMetaInfoService):
    '''
    Provides the service methods for the meta info image.
    '''
