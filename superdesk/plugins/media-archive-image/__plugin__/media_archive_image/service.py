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

# --------------------------------------------------------------------

imageDataHandler = ioc.getEntity('imageDataHandler', service)

@ioc.replace(ioc.getEntity(IImageDataService, service))
def imageData() -> IImageDataService:
    b = ImageDataServiceAlchemy()
    b.handler = imageDataHandler()
    return b

