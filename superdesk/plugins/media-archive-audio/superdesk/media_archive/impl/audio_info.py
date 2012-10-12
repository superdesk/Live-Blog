'''
Created on Aug 23, 2012

@package: superdesk media archive
@copyright: 2012 Sourcefabric o.p.s.
@license: http://www.gnu.org/licenses/gpl-3.0.txt
@author: Ioan v. Pocol

SQL Alchemy based implementation for the audio data API. 
'''

from ..api.audio_data import QAudioData
from ..api.audio_info import IAudioInfoService, QAudioInfo
from ..meta.audio_data import AudioDataMapped
from ..meta.audio_info import AudioInfoMapped
from .meta_info import MetaInfoServiceBaseAlchemy
from ally.container.ioc import injected
from ally.container.support import setup
from superdesk.media_archive.core.spec import QueryIndexer
from ally.container import wire
from superdesk.media_archive.meta.audio_info import AudioInfoEntry
from superdesk.media_archive.meta.audio_data import AudioDataEntry


# --------------------------------------------------------------------

@injected
@setup(IAudioInfoService)
class AudioInfoServiceAlchemy(MetaInfoServiceBaseAlchemy, IAudioInfoService):
    '''
    @see: IAudioInfoService
    '''
    
    queryIndexer = QueryIndexer;wire.entity('queryIndexer')

    def __init__(self):
        MetaInfoServiceBaseAlchemy.__init__(self, AudioInfoMapped, QAudioInfo, AudioDataMapped, QAudioData)
        self.queryIndexer.register(AudioInfoEntry, QAudioInfo, AudioDataEntry, QAudioData)
        