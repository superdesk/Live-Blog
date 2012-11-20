'''
Created on Oct 1, 2012

@package: superdesk media archive
@copyright: 2012 Sourcefabric o.p.s.
@license: http://www.gnu.org/licenses/gpl-3.0.txt
@author: Ioan v. Pocol

API specifications for media archive audio info.
'''

from .domain_archive import modelArchive
from .audio_data import AudioData, QAudioData
from .meta_data import MetaData, QMetaData
from .meta_info import MetaInfo, QMetaInfo, IMetaInfoService
from ally.api.config import query, service
from ally.api.criteria import AsLikeOrdered

# --------------------------------------------------------------------

@modelArchive
class AudioInfo(MetaInfo):
    '''
    Provides the meta info audio.
    '''
    MetaData = AudioData
    Caption = str

# --------------------------------------------------------------------

@query(AudioInfo)
class QAudioInfo(QMetaInfo):
    '''
    The query for audio info model.
    '''
    caption = AsLikeOrdered

# --------------------------------------------------------------------

@service((MetaInfo, AudioInfo), (QMetaInfo, QAudioInfo), (MetaData, AudioData), (QMetaData, QAudioData))
class IAudioInfoService(IMetaInfoService):
    '''
    Provides the service methods for the meta info audio.
    '''
