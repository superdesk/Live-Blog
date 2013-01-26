'''
Created on Apr 19, 2012

@package: superdesk media archive
@copyright: 2012 Sourcefabric o.p.s.
@license: http://www.gnu.org/licenses/gpl-3.0.txt
@author: Gabriel Nistor

API specifications for media archive image info.
'''

from ally.api.config import query, service, model
from superdesk.media_archive.api.criteria import AsLikeExpressionOrdered
from superdesk.media_archive.api.image_data import ImageData, QImageData
from superdesk.media_archive.api.meta_data import MetaData, QMetaData
from superdesk.media_archive.api.meta_info import MetaInfo, QMetaInfo, \
    IMetaInfoService

# --------------------------------------------------------------------

@model
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
    caption = AsLikeExpressionOrdered

# --------------------------------------------------------------------

@service((MetaInfo, ImageInfo), (QMetaInfo, QImageInfo), (MetaData, ImageData), (QMetaData, QImageData))
class IImageInfoService(IMetaInfoService):
    '''
    Provides the service methods for the meta info image.
    '''
