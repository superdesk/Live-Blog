'''
Created on Oct 1, 2012

@package: superdesk media archive
@copyright: 2012 Sourcefabric o.p.s.
@license: http://www.gnu.org/licenses/gpl-3.0.txt
@author: Ioan v. Pocol

SQL Alchemy based implementation for the audio data API. 
'''

from ally.cdm.spec import ICDM
from ally.container import wire
from ally.container.ioc import injected
from ally.container.support import setup
from superdesk.media_archive.api.audio_data import IAudioDataService, QAudioData
from superdesk.media_archive.core.impl.meta_service_base import \
    MetaDataServiceBaseAlchemy
from superdesk.media_archive.core.spec import IMetaDataReferencer, \
    IThumbnailManager
from superdesk.media_archive.meta.audio_data import AudioDataMapped

# --------------------------------------------------------------------

@injected
@setup(IAudioDataService, name='audioDataService')
class AudioDataServiceAlchemy(MetaDataServiceBaseAlchemy, IMetaDataReferencer, IAudioDataService):
    '''
    Implementation for see @see: IAudioDataService
    '''
    
    cdmArchiveAudio = ICDM; wire.entity('cdmArchiveAudio')
    thumbnailManager = IThumbnailManager; wire.entity('thumbnailManager')

    def __init__(self):
        assert isinstance(self.cdmArchiveAudio, ICDM), 'Invalid archive CDM %s' % self.cdmArchiveAudio
        assert isinstance(self.thumbnailManager, IThumbnailManager), 'Invalid thumbnail manager %s' % self.thumbnailManager
       
        MetaDataServiceBaseAlchemy.__init__(self, AudioDataMapped, QAudioData, self, self.cdmArchiveAudio, self.thumbnailManager)
    
