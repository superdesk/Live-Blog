'''
Created on Apr 25, 2012

@package: superdesk media archive
@copyright: 2012 Sourcefabric o.p.s.
@license: http://www.gnu.org/licenses/gpl-3.0.txt
@author: Gabriel Nistor

Contains the services setups for media archive superdesk.
'''

from ..cdm.local_cdm import contentDeliveryManager
from ..superdesk import service
from ..superdesk.db_superdesk import createTables
from ally.container import ioc, support
from cdm.spec import ICDM
from cdm.support import ExtendPathCDM
from superdesk.media_archive.api.meta_data import IMetaDataService
from superdesk.media_archive.core.impl.thumbnail_referencer import \
    ThumbnailReferencer
from superdesk.media_archive.core.spec import IThumbnailReferencer, \
    IThumbnailManager, IThumbnailCreator
from superdesk.media_archive.impl.meta_data import IMetaDataHandler, \
    MetaDataServiceAlchemy
from __plugin__.plugin.registry import cdmGUI
import logging
from superdesk.media_archive.core.impl.thumbnail_manager import ThumbnailManager, \
    ThumbnailCreatorFFMpeg

# --------------------------------------------------------------------

log = logging.getLogger(__name__)

# --------------------------------------------------------------------

def addMetaDataHandler(handler):
    if not isinstance(handler, IMetaDataService): metaDataHandlers().append(handler)

support.listenToEntities(IMetaDataHandler, listeners=addMetaDataHandler, setupModule=service, beforeBinding=False)

# --------------------------------------------------------------------

@ioc.entity
def thumbnail_sizes():
    '''
    Contains the thumbnail sizes available for the media archive.
    This is basically just a simple dictionary{string, tuple(integer, integer)} that has as a key a path safe name
    and as a value a tuple with the width/height of the thumbnail.
    example: {'small': [100, 100]}
    '''
    return { 'tiny' : [16, 16], 'small' : [32, 32], 'medium' : [64, 64], 'large' : [128, 128], 'huge' : [256, 256] }

# --------------------------------------------------------------------

@ioc.entity
def cdmArchive() -> ICDM:
    '''
    The content delivery manager (CDM) for the media archive.
    '''
    return ExtendPathCDM(contentDeliveryManager(), 'media_archive/%s')

@ioc.entity
def cdmThumbnail() -> ICDM:
    '''
    The content delivery manager (CDM) for the thumbnails media archive.
    '''
    return ExtendPathCDM(contentDeliveryManager(), 'media_archive/thumbnail/%s')

@ioc.entity
def thumbnailReferencer() -> IThumbnailReferencer:
    b = ThumbnailReferencer()
    b.cdmThumbnail = cdmThumbnail()
    b.thumbnailSizes = thumbnail_sizes()
    return b

@ioc.entity
def thumbnailManager() -> IThumbnailManager:
    b = ThumbnailManager()
    b.thumbnailSizes = thumbnail_sizes()
    b.thumbnailCreator = thumbnailCreator()
    b.cdmThumbnail = cdmThumbnail()
    return b

@ioc.entity
def thumbnailCreator() -> IThumbnailCreator:
    return ThumbnailCreatorFFMpeg()

@ioc.entity
def metaDataService() -> IMetaDataService:
    b = MetaDataServiceAlchemy()
    b.cdmArchive = cdmArchive()
    b.metaDataHandlers = metaDataHandlers()
    return b

# --------------------------------------------------------------------

@ioc.entity
def metaDataHandlers(): return []

# --------------------------------------------------------------------

@ioc.after(createTables)
def deploy():
    metaDataService().deploy()

@ioc.start
def publish():
    publishResources()

# --------------------------------------------------------------------

def publishResources():
    '''
    Publishes media archive plugin resources.
    '''
    log.info('published library %s = %s')
    #TODO: 
    #cdmGUI().publishFromDir('media-archive/upload', 'resourcesPath')
