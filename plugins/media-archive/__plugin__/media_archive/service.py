'''
Created on Apr 25, 2012

@package: superdesk media archive
@copyright: 2012 Sourcefabric o.p.s.
@license: http://www.gnu.org/licenses/gpl-3.0.txt
@author: Gabriel Nistor

Contains the services setups for media archive superdesk.
'''

from ..plugin.registry import registerService
from ..superdesk import service
from ally.cdm.impl.local_filesystem import LocalFileSystemCDM, HTTPDelivery, \
    IDelivery
from ally.cdm.spec import ICDM
from ally.cdm.support import ExtendPathCDM
from ally.container import ioc, support, bind, app, wire
from superdesk.media_archive.api.meta_data import IMetaDataService
from superdesk.media_archive.core.impl.db_search import SqlSearchProvider
from superdesk.media_archive.core.impl.query_service_creator import \
    createService, ISearchProvider
from superdesk.media_archive.core.impl.thumbnail_processor_avconv import \
    ThumbnailProcessorAVConv
from superdesk.media_archive.core.impl.thumbnail_processor_ffmpeg import \
    ThumbnailProcessorFfmpeg
from superdesk.media_archive.core.impl.thumbnail_processor_gm import \
    ThumbnailProcessorGM
from superdesk.media_archive.core.spec import IThumbnailManager, QueryIndexer, \
    IQueryIndexer, IThumbnailProcessor
from superdesk.media_archive.impl.meta_data import IMetaDataHandler
from ..superdesk.database import binders
from ..cdm.service import server_uri, repository_path
from ally.container.support import nameInEntity
from ally.container.ioc import entityOf
import logging
from collections import OrderedDict
from os import getenv, access, F_OK, R_OK, X_OK
from os.path import join

# --------------------------------------------------------------------
log = logging.getLogger(__name__)

# --------------------------------------------------------------------

def addMetaDataHandler(handler):
    if not isinstance(handler, IMetaDataService): metaDataHandlers().append(handler)

bind.bindToEntities('superdesk.media_archive.core.impl.**.*Alchemy', binders=binders)
support.createEntitySetup('superdesk.media_archive.core.impl.**.*')
support.listenToEntities(IMetaDataHandler, listeners=addMetaDataHandler, beforeBinding=False, module=service)
support.loadAllEntities(IMetaDataHandler, module=service)

# --------------------------------------------------------------------

@ioc.config
def use_solr_search():
    ''' If true then the media archive search is made using solr'''
    return False

@ioc.config
def thumnail_processor():
    '''
    Specify which implementation will be used for thumbnail processor. Currently the following options are available:
        "gm", "ffmpeg", "avconv"
    '''

# --------------------------------------------------------------------

@ioc.entity
def searchProvider() -> ISearchProvider:

    if use_solr_search():
        from superdesk.media_archive.core.impl.solr_search import SolrSearchProvider
        b = SolrSearchProvider()
    else:
        b = SqlSearchProvider()

    return b

@ioc.entity
def delivery() -> IDelivery:
    d = HTTPDelivery()
    d.serverURI = server_uri()
    d.repositoryPath = repository_path()
    return d

@ioc.entity
def contentDeliveryManager() -> ICDM:
    cdm = LocalFileSystemCDM();
    cdm.delivery = delivery()
    return cdm

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
def metaDataHandlers() -> list: return []

@ioc.entity
def queryIndexer() -> IQueryIndexer: return QueryIndexer()

@wire.wire(ThumbnailProcessorFfmpeg, ThumbnailProcessorAVConv, ThumbnailProcessorGM)
@ioc.entity
def thumbnailProcessor() -> IThumbnailProcessor: 
    if thumnail_processor() == 'ffmpeg':
        return ThumbnailProcessorFfmpeg()
    elif thumnail_processor() == 'avconv':
        return ThumbnailProcessorAVConv()
    else:
        return ThumbnailProcessorGM()

# --------------------------------------------------------------------

@app.deploy
def publishQueryService():
    b = createService(queryIndexer(), cdmArchive(), support.entityFor(IThumbnailManager), searchProvider())
    registerService(b, binders())

@app.dump
def processBinaryRequirements():
    processors = OrderedDict(PROCESSORS)
    proc = thumnail_processor()
    try:
        detector, pathSetup = processors.pop(proc)
    except KeyError:
        log.error('Invalid thumbnail processor %s', proc)
        proc, (detector, pathSetup) = processors.popitem(last=False)
        log.info('Chosing the thumbnail processor with the higher priority: %s', proc)

    binPath = detector(pathSetup())
    
    if binPath is None:
        for proc, (detector, pathSetup) in processors.items():
            binPath = detector(pathSetup())
            if binPath is not None: break
    
        if binPath is None:
            log.error('Unable to find any binary for thubmnail processing')
            return

    if proc != thumnail_processor():
        log.info('Chosing the thumbnail processor: %s', proc)
        support.persist(thumnail_processor, proc)

    if pathSetup() != binPath:
        support.persist(pathSetup, binPath)

# --------------------------------------------------------------------

def detectBinPath(binNames):
    for path in getenv('PATH').split(':'):
        for binName in binNames:
            binPath = join(path, binName)
            if access(binPath, F_OK | R_OK | X_OK):
                return binPath
    return None

def detectFFMpegPath(defaultPath=None):
    if access(defaultPath, F_OK | R_OK | X_OK):
        return defaultPath
    return detectBinPath(('ffmpeg', 'ffmpeg.exe'))

def detectAVConvPath(defaultPath=None):
    if access(defaultPath, F_OK | R_OK | X_OK):
        return defaultPath
    return detectBinPath(('avconv', 'avconv.exe'))

def detectGMPath(defaultPath=None):
    if access(defaultPath, F_OK | R_OK | X_OK):
        return defaultPath
    return detectBinPath(('gm', 'gm.exe'))

PROCESSORS = (
('gm', (detectGMPath, entityOf(nameInEntity(ThumbnailProcessorGM, 'gm_path', location=thumbnailProcessor)))),
('avconv', (detectAVConvPath, entityOf(nameInEntity(ThumbnailProcessorAVConv, 'avconv_path', location=thumbnailProcessor)))),
('ffmpeg', (detectFFMpegPath, entityOf(nameInEntity(ThumbnailProcessorFfmpeg, 'ffmpeg_path', location=thumbnailProcessor)))),
)
