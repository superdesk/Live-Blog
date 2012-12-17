'''
Created on Oct 1, 2012

@package: superdesk media archive
@copyright: 2012 Sourcefabric o.p.s.
@license: http://www.gnu.org/licenses/gpl-3.0.txt
@author: Ioan v. Pocol

API specifications for media meta data audio archive.
'''

from ally.api.config import query, service
from superdesk.media_archive.api.domain_archive import modelArchive
from superdesk.media_archive.api.meta_data import QMetaData, IMetaDataService,\
    MetaData
from superdesk.media_archive.api.criteria import AsEqualExpressionOrdered, \
    AsLikeExpressionOrdered

# --------------------------------------------------------------------

@modelArchive
class AudioData(MetaData):
    '''
    Provides the meta data that is extracted based on the content.
    '''

    Length = int
    AudioEncoding = str
    SampleRate = int
    Channels = str
    AudioBitrate = int
    
    Title = str
    Artist = str
    Track = int
    Album = str
    Genre = str
    #Part of a compilation 1 - True, 0 - False
    Tcmp = int
    AlbumArtist = str
    Year = int
    Disk = int
    #Beats-per-minute
    Tbpm = int
    Composer = str

# --------------------------------------------------------------------

@query(AudioData)
class QAudioData(QMetaData):
    '''
    The query for audio model.
    '''
    length = AsEqualExpressionOrdered
    audioEncoding = AsLikeExpressionOrdered
    sampleRate = AsEqualExpressionOrdered
    channels = AsLikeExpressionOrdered
    audioBitrate = AsEqualExpressionOrdered
    
    title = AsLikeExpressionOrdered
    artist = AsLikeExpressionOrdered
    track = AsEqualExpressionOrdered
    album = AsLikeExpressionOrdered
    genre = AsLikeExpressionOrdered
    #Part of a compilation 1 - True, 0 - False
    tcmp = AsEqualExpressionOrdered
    albumArtist = AsLikeExpressionOrdered
    year = AsEqualExpressionOrdered
    disk = AsEqualExpressionOrdered
    #Beats-per-minute
    tbpm = AsEqualExpressionOrdered
    composer = AsLikeExpressionOrdered

# --------------------------------------------------------------------

@service((MetaData, AudioData), (QMetaData, QAudioData))
class IAudioDataService(IMetaDataService):
    '''
    Provides the service methods for the meta data audio.
    '''
