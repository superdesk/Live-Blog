'''
Created on Oct 1, 2012

@package: superdesk media archive
@copyright: 2012 Sourcefabric o.p.s.
@license: http://www.gnu.org/licenses/gpl-3.0.txt
@author: Ioan v. Pocol

SQL Alchemy based implementation for the audio data API. 
'''

from ..api.audio_data import QAudioData
from ..meta.audio_data import AudioDataMapped
from .meta_data import MetaDataServiceBaseAlchemy
from ally.container.ioc import injected
from ally.container.support import setup
from superdesk.media_archive.core.spec import IMetaDataHandler, IMetaDataReferencer
from superdesk.media_archive.api.audio_data import IAudioDataService

# --------------------------------------------------------------------

@injected
@setup(IAudioDataService)
class AudioDataServiceAlchemy(MetaDataServiceBaseAlchemy, IMetaDataReferencer, IAudioDataService):
    '''
    @see: IAudioDataService
    '''

    handler = IMetaDataHandler

    def __init__(self):
        assert isinstance(self.handler, IMetaDataHandler), \
        'Invalid handler %s' % self.handler
        MetaDataServiceBaseAlchemy.__init__(self, AudioDataMapped, QAudioData, self)
    
    # ----------------------------------------------------------------

    def populate(self, metaData, scheme, thumbSize=None):
        
        return metaData
