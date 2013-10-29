'''
Created on Aug 23, 2012

@package: superdesk media archive video
@copyright: 2012 Sourcefabric o.p.s.
@license: http://www.gnu.org/licenses/gpl-3.0.txt
@author: Ioan v. Pocol

Contains the services setups for media video archive.
'''

from ally.cdm.spec import ICDM
from ally.cdm.support import ExtendPathCDM
from ..cdm.service import contentDeliveryManager
from ally.container import ioc, app, support
from ally.container.support import nameInEntity
from ally.container.ioc import entityOf
from superdesk.media_archive.impl.video_persist import VideoPersistanceAlchemy
from ..media_archive.service import detectFFMpegPath
import logging

# --------------------------------------------------------------------

log = logging.getLogger(__name__)

# --------------------------------------------------------------------

@ioc.entity
def cdmArchiveVideo() -> ICDM:
    '''
    The content delivery manager (CDM) for the media archive.
    '''
    return ExtendPathCDM(contentDeliveryManager(), 'media_archive/%s')

@app.dump
def processBinaryRequirements():
    videoMetaProcessorSetup = entityOf(nameInEntity(VideoPersistanceAlchemy, 'ffmpeg_path'))
    binPath = detectFFMpegPath(videoMetaProcessorSetup())
    if binPath is None:
        log.error('Unable to find any binary for audio metadata processing')
        return
    if binPath != videoMetaProcessorSetup():
        log.info('Setting video meta processor to %s', binPath)
        support.persist(videoMetaProcessorSetup, binPath)
