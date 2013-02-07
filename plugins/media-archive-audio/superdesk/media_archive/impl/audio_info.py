'''
Created on Aug 23, 2012

@package: superdesk media archive
@copyright: 2012 Sourcefabric o.p.s.
@license: http://www.gnu.org/licenses/gpl-3.0.txt
@author: Ioan v. Pocol

SQL Alchemy based implementation for the audio data API.
'''

from ally.container import wire
from ally.container.ioc import injected
from ally.container.support import setup
from superdesk.media_archive.api.audio_data import QAudioData, IAudioDataService
from superdesk.media_archive.api.audio_info import IAudioInfoService, QAudioInfo
from superdesk.media_archive.core.impl.meta_service_base import \
    MetaInfoServiceBaseAlchemy
from superdesk.media_archive.core.spec import IQueryIndexer
from superdesk.media_archive.meta.audio_data import AudioDataEntry, \
    AudioDataMapped, META_TYPE_KEY
from superdesk.media_archive.meta.audio_info import AudioInfoMapped, \
    AudioInfoEntry
from superdesk.media_archive.core.impl.query_service_creator import ISearchProvider


# --------------------------------------------------------------------

@injected
@setup(IAudioInfoService)
class AudioInfoServiceAlchemy(MetaInfoServiceBaseAlchemy, IAudioInfoService):
    '''
    @see: IAudioInfoService
    '''

    queryIndexer = IQueryIndexer;wire.entity('queryIndexer')
    # The query indexer manages the query related information about plugins in order to be able to support the multi-plugin queries
    searchProvider = ISearchProvider; wire.entity('searchProvider')
    # The search provider that will be used to manage all search related activities
    audioDataService = IAudioDataService; wire.entity('audioDataService')
    #The correspondent meta data service for audio

    def __init__(self):
        assert isinstance(self.queryIndexer, IQueryIndexer), 'Invalid IQueryIndexer %s' % self.queryIndexer
        assert isinstance(self.searchProvider, ISearchProvider), 'Invalid search provider %s' % self.searchProvider
        assert isinstance(self.audioDataService, IAudioDataService), 'Invalid audio meta data service %s' % self.audioDataService

        MetaInfoServiceBaseAlchemy.__init__(self, AudioInfoMapped, QAudioInfo, AudioDataMapped, QAudioData, 
                                            self.searchProvider, self.audioDataService, META_TYPE_KEY)
        
        self.queryIndexer.register(AudioInfoEntry, QAudioInfo, AudioDataEntry, QAudioData, META_TYPE_KEY)

