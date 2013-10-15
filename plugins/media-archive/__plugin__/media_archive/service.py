'''
Created on Apr 25, 2012

@package: superdesk media archive
@copyright: 2012 Sourcefabric o.p.s.
@license: http://www.gnu.org/licenses/gpl-3.0.txt
@author: Gabriel Nistor

Contains the services setups for media archive superdesk.
'''

from ..cdm import server_uri, repository_path
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

# --------------------------------------------------------------------

@ioc.entity
def searchProvider() -> ISearchProvider:

    if use_solr_search():
        from superdesk.media_archive.core.impl.solr_search import SolrSearchProvider
        b = SolrSearchProvider()
    else:
        b = SqlSearchProvider()

    return b

# --------------------------------------------------------------------

@ioc.entity
def delivery() -> IDelivery:
    d = HTTPDelivery()
    d.serverURI = server_uri()
    d.repositoryPath = repository_path()
    return d

# --------------------------------------------------------------------

@ioc.entity
def contentDeliveryManager() -> ICDM:
    cdm = LocalFileSystemCDM();
    cdm.delivery = delivery()
    return cdm

# --------------------------------------------------------------------

@ioc.entity
def cdmArchive() -> ICDM:
    '''
    The content delivery manager (CDM) for the media archive.
    '''
    return ExtendPathCDM(contentDeliveryManager(), 'media_archive/%s')

# --------------------------------------------------------------------

@ioc.entity
def cdmThumbnail() -> ICDM:
    '''
    The content delivery manager (CDM) for the thumbnails media archive.
    '''
    return ExtendPathCDM(contentDeliveryManager(), 'media_archive/thumbnail/%s')

# --------------------------------------------------------------------

@ioc.entity
def metaDataHandlers() -> list: return []

# --------------------------------------------------------------------

@ioc.entity
def queryIndexer() -> IQueryIndexer: return QueryIndexer()

# --------------------------------------------------------------------

@ioc.config
def thumnail_processor():
    '''
    Specify which implementation will be used for thumbnail processor. Currently the following options are available:
        "gm", "ffmpeg", "avconv"
    '''

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
