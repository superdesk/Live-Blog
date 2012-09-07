'''
Created on Aug 23, 2012

@package: superdesk media archive image
@copyright: 2012 Sourcefabric o.p.s.
@license: http://www.gnu.org/licenses/gpl-3.0.txt
@author: Ioan v. Pocol

Contains the services setups for media image archive.
'''

from ally.container import ioc
from ..superdesk.db_superdesk import createTables
from superdesk.media_archive.api.image_data import IImageDataService
from superdesk.media_archive.impl.image_data import ImageDataServiceAlchemy
from __plugin__.superdesk import service

# --------------------------------------------------------------------

imageDataHandler = ioc.getEntity('imageDataHandler', service)
@ioc.replace(ioc.getEntity(IImageDataService, service))
def imageData() -> IImageDataService:
    b = ImageDataServiceAlchemy()
    b.handler = imageDataHandler()
    return b
#    return b
@ioc.after(createTables)
def deploy():
    imageDataHandler().deploy()
    
#@ioc.start
#def register():
#    registerService(imageData())
#    registerService(imageInfo())
    

# --------------------------------------------------------------------

@ioc.after(createTables)
def deploy():
    imageDataHandler().deploy()