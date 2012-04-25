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
from ally.container import ioc, support
from cdm.spec import ICDM
from cdm.support import ExtendPathCDM
from superdesk.media_archive.impl.meta_data import MetaDataReferenceHandlers, \
    IMetaDataReferenceHandler

# --------------------------------------------------------------------

def addMetaDataReferenceHandler(handler):
    metaDataReferenceHandlers().append(handler)

support.listenToEntities(IMetaDataReferenceHandler, listeners=addMetaDataReferenceHandler, \
                         setupModule=service, beforeBinding=False)

# --------------------------------------------------------------------

@ioc.entity
def cdmArchive() -> ICDM:
    '''
    The content delivery manager (CDM) for the media archive.
    '''
    return ExtendPathCDM(contentDeliveryManager(), 'media_archive/%s')

@ioc.entity
def cdmArchiveThumbnail() -> ICDM:
    '''
    The content delivery manager (CDM) for the thumbnails media archive.
    '''
    return ExtendPathCDM(contentDeliveryManager(), 'media_archive/thumbnail/%s')

@ioc.entity
def metaDataReferenceHandlers() -> MetaDataReferenceHandlers:
    return MetaDataReferenceHandlers()
