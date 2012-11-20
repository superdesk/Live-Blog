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

# --------------------------------------------------------------------

audioDataHandler = ioc.getEntity('audioDataHandler', service)

@ioc.replace(ioc.getEntity(IAudioDataService, service))
def audioData() -> IAudioDataService:
    b = AudioDataServiceAlchemy()
    b.handler = audioDataHandler()
    return b
