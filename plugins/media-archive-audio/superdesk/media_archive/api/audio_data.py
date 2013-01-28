'''
Created on Oct 1, 2012

@package: superdesk media archive
@copyright: 2012 Sourcefabric o.p.s.
@license: http://www.gnu.org/licenses/gpl-3.0.txt
@author: Ioan v. Pocol

API specifications for media meta data audio archive.
'''

from ally.api.config import query, service, model
from ally.api.criteria import AsRangeOrdered, AsEqualOrdered, AsLikeOrdered
from superdesk.media_archive.api.criteria import AsLikeExpressionOrdered
from superdesk.media_archive.api.meta_data import QMetaData, IMetaDataService, \
    MetaData

# --------------------------------------------------------------------

@model
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
    length = AsRangeOrdered
    audioEncoding = AsLikeOrdered
    sampleRate = AsRangeOrdered
    channels = AsLikeOrdered
    audioBitrate = AsRangeOrdered
    
    title = AsLikeExpressionOrdered
    artist = AsLikeExpressionOrdered
    track = AsRangeOrdered
    album = AsLikeExpressionOrdered
    genre = AsLikeExpressionOrdered
    #Part of a compilation 1 - True, 0 - False
    tcmp = AsEqualOrdered
    albumArtist = AsLikeExpressionOrdered
    year = AsRangeOrdered
    disk = AsRangeOrdered
    #Beats-per-minute
    tbpm = AsRangeOrdered
    composer = AsLikeExpressionOrdered

# --------------------------------------------------------------------

@service((MetaData, AudioData), (QMetaData, QAudioData))
class IAudioDataService(IMetaDataService):
    '''
    Provides the service methods for the meta data audio.
    '''
