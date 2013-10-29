'''
Created on Oct 1, 2012

@package: superdesk media archive audio
@copyright: 2012 Sourcefabric o.p.s.
@license: http://www.gnu.org/licenses/gpl-3.0.txt
@author: Ioan v. Pocol

Contains the services setups for media audio archive.
'''

from ..cdm.service import contentDeliveryManager
from ally.cdm.spec import ICDM
from ally.cdm.support import ExtendPathCDM
from ally.container import ioc, app, support
from ally.container.support import nameInEntity
from ally.container.ioc import entityOf
from superdesk.media_archive.impl.audio_persist import AudioPersistanceAlchemy
from ..media_archive.service import detectFFMpegPath
import logging

# --------------------------------------------------------------------

log = logging.getLogger(__name__)

# --------------------------------------------------------------------

@ioc.entity
def cdmArchiveAudio() -> ICDM:
    '''
    The content delivery manager (CDM) for the media archive.
    '''
    return ExtendPathCDM(contentDeliveryManager(), 'media_archive/%s')

@app.dump
def processBinaryRequirements():
    audioMetaProcessorSetup = entityOf(nameInEntity(AudioPersistanceAlchemy, 'ffmpeg_path'))
    binPath = detectFFMpegPath(audioMetaProcessorSetup())
    if binPath is None:
        log.error('Unable to find any binary for audio metadata processing')
        return
    if binPath != audioMetaProcessorSetup():
        log.info('Setting audio meta processor to %s', binPath)
        support.persist(audioMetaProcessorSetup, binPath)
