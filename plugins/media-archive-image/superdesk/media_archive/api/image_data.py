'''
Created on Apr 17, 2012

@package: superdesk media archive
@copyright: 2012 Sourcefabric o.p.s.
@license: http://www.gnu.org/licenses/gpl-3.0.txt
@author: Gabriel Nistor

API specifications for media meta data image archive.
'''

from .domain_archive import modelArchive
from .meta_data import MetaData, QMetaData, IMetaDataService
from ally.api.config import query, service
from ally.api.criteria import AsEqualOrdered, AsDateTimeOrdered, AsLikeOrdered
from datetime import datetime

# --------------------------------------------------------------------

@modelArchive
class ImageData(MetaData):
    '''
    Provides the meta data that is extracted based on the content.
    '''
    Width = int
    Height = int
    CreationDate = datetime
    CameraMake = str
    CameraModel = str


# --------------------------------------------------------------------

@query(ImageData)
class QImageData(QMetaData):
    '''
    The query for image model.
    '''
    width = AsEqualOrdered
    height = AsEqualOrdered
    creationDate = AsDateTimeOrdered
    cameraMake = AsLikeOrdered
    cameraModel = AsLikeOrdered

# --------------------------------------------------------------------

@service((MetaData, ImageData), (QMetaData, QImageData))
class IImageDataService(IMetaDataService):
    '''
    Provides the service methods for the meta data image.
    '''
