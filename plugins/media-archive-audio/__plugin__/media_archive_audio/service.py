'''
Created on Oct 1, 2012

@package: superdesk media archive audio
@copyright: 2012 Sourcefabric o.p.s.
@license: http://www.gnu.org/licenses/gpl-3.0.txt
@author: Ioan v. Pocol

Contains the services setups for media audio archive.
'''

from ..superdesk import service
from ally.container import ioc
from superdesk.media_archive.api.audio_data import IAudioDataService
from superdesk.media_archive.impl.audio_data import AudioDataServiceAlchemy
from cdm.spec import ICDM
from __plugin__.cdm.local_cdm import contentDeliveryManager
from cdm.support import ExtendPathCDM

# --------------------------------------------------------------------

audioDataHandler = ioc.getEntity('audioDataHandler', service)

@ioc.entity
def cdmArchive() -> ICDM:
    '''
    The content delivery manager (CDM) for the media archive.
    '''
    return ExtendPathCDM(contentDeliveryManager(), 'media_archive/%s')

@ioc.replace(ioc.getEntity(IAudioDataService, service))
def audioData() -> IAudioDataService:
    b = AudioDataServiceAlchemy()
    b.cdmArchive = cdmArchive()
    b.handler = audioDataHandler()
    return b
