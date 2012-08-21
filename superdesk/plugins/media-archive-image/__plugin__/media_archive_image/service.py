'''
Created on Apr 25, 2012

@package: superdesk media archive image
@copyright: 2012 Sourcefabric o.p.s.
@license: http://www.gnu.org/licenses/gpl-3.0.txt
@author: Gabriel Nistor

Contains the services setups for media image archive.
'''

from ally.container import ioc
from ..superdesk.db_superdesk import createTables
from superdesk.media_archive.api.image_data import IImageDataService
from superdesk.media_archive.api.image_info import IImageInfoService
from superdesk.media_archive.api.image_persist import IImagePersistanceService
from superdesk.media_archive.impl.image_data import ImageDataServiceAlchemy
from superdesk.media_archive.impl.image_info import ImageInfoServiceAlchemy
from superdesk.media_archive.impl.image_persist import ImagePersistanceService
from superdesk.media_archive.core.spec import IMetaDataHandler


# --------------------------------------------------------------------

@ioc.entity
def imagePersistanceService() -> IImagePersistanceService:
    b = ImagePersistanceService()
    return b

# --------------------------------------------------------------------

@ioc.entity
def imageDataHandler() -> IMetaDataHandler:
    return imagePersistanceService()

# --------------------------------------------------------------------

@ioc.entity
def imageData() -> IImageDataService:
    b = ImageDataServiceAlchemy()
    b.handler = imageDataHandler()
    return b


@ioc.entity
def imageInfo() -> IImageInfoService:
    b = ImageInfoServiceAlchemy()
    return b

# --------------------------------------------------------------------

@ioc.after(createTables)
def deploy():
    imagePersistanceService().deploy()


# --------------------------------------------------------------------
