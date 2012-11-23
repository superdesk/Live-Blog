'''
Created on Aug 23, 2012

@package: superdesk media archive image
@copyright: 2012 Sourcefabric o.p.s.
@license: http://www.gnu.org/licenses/gpl-3.0.txt
@author: Ioan v. Pocol

Contains the services setups for media image archive.
'''

from ..superdesk import service
from ally.container import ioc
from superdesk.media_archive.api.image_data import IImageDataService
from superdesk.media_archive.impl.image_data import ImageDataServiceAlchemy
from cdm.spec import ICDM
from __plugin__.cdm.local_cdm import contentDeliveryManager
from cdm.support import ExtendPathCDM

# --------------------------------------------------------------------

imageDataHandler = ioc.getEntity('imageDataHandler', service)

@ioc.entity
def cdmArchive() -> ICDM:
    '''
    The content delivery manager (CDM) for the media archive.
    '''
    return ExtendPathCDM(contentDeliveryManager(), 'media_archive/%s')

@ioc.replace(ioc.getEntity(IImageDataService, service))
def imageData() -> IImageDataService:
    b = ImageDataServiceAlchemy()
    b.cdmArchive = cdmArchive()
    b.handler = imageDataHandler()
    return b

