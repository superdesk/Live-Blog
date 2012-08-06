'''
Created on Apr 25, 2012

@package: superdesk media archive image
@copyright: 2012 Sourcefabric o.p.s.
@license: http://www.gnu.org/licenses/gpl-3.0.txt
@author: Gabriel Nistor

Contains the services setups for media image archive.
'''

from ..media_archive.service import cdmArchive, cdmArchiveThumbnail
from ally.container import ioc
from cdm.spec import ICDM
from cdm.support import ExtendPathCDM
from superdesk.media_archive.api.image_data import IImageDataService
from superdesk.media_archive.api.image_persist import IImagePersistanceService
from superdesk.media_archive.impl.image_data import ImageDataServiceAlchemy
from superdesk.media_archive.impl.image_persist import ImagePersistanceService
from superdesk.media_archive.impl.meta_data import IMetaDataReferenceHandler
from __plugin__.media_archive.service import thumbnail_sizes

# --------------------------------------------------------------------

@ioc.entity
def cdmArchiveImage() -> ICDM:
    return ExtendPathCDM(cdmArchive(), 'image/%s')

@ioc.entity
def cdmArchiveThumbnailImage() -> ICDM:
    return ExtendPathCDM(cdmArchiveThumbnail(), 'image/%s')

@ioc.entity
def imagePersistance() -> IImagePersistanceService:
    b = ImagePersistanceService()
    b.thumbnailSizes = thumbnail_sizes()
    b.cdmImages = cdmArchiveImage()
    b.cdmThumbnails = cdmArchiveThumbnailImage()
    return b

@ioc.entity
def imageDataReferenceHandler() -> IMetaDataReferenceHandler:
    return imagePersistance()

@ioc.entity
def imageData() -> IImageDataService:
    b = ImageDataServiceAlchemy()
    b.referenceHandler = imageDataReferenceHandler()
    return b
