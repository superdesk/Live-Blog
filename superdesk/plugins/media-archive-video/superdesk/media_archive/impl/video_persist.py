'''
Created on Aug 23, 2012

@package: superdesk media archive
@copyright: 2012 Sourcefabric o.p.s.
@license: http://www.gnu.org/licenses/gpl-3.0.txt
@author: Ioan v. Pocol

Implementation for the video persistence API.
'''

from ally.container import wire
from ally.container.ioc import injected
from ally.container.support import setup
from ally.support.sqlalchemy.session import SessionSupport
from ally.support.sqlalchemy.util_service import handle
from ally.support.util_io import timestampURI
from ally.support.util_sys import pythonPath
from ..core.spec import IThumbnailManager
from ..meta.video_data import VideoDataEntry
from ..meta.meta_data import MetaDataMapped
from superdesk.media_archive.core.impl.meta_service_base import thumbnailFormatFor, metaTypeFor
from superdesk.media_archive.core.spec import IMetaDataHandler
from sqlalchemy.exc import SQLAlchemyError
from os.path import join, exists
from os import remove
from subprocess import Popen, PIPE, STDOUT


# --------------------------------------------------------------------

@injected
@setup(IMetaDataHandler, 'videoDataHandler')
class VideoPersistanceAlchemy(SessionSupport, IMetaDataHandler):
    '''
    Provides the service that handles the video persistence @see: IVideoPersistanceService.
    '''

    format_file_name = '%(id)s.%(file)s'; wire.config('format_file_name', doc='''
    The format for the videos file names in the media archive''')
    video_supported_files = 'flv, avi, mov, mp4, mpg, wmv, 3gp, asf, rm, swf';wire.config('video_supported_files', doc='''
    The video formats supported by media archive video plugin''')

    videoType = 'video'
    # The type for the meta type video

    thumbnailManager = IThumbnailManager; wire.entity('thumbnailManager')
    # Provides the thumbnail referencer

    def __init__(self):
        assert isinstance(self.format_file_name, str), 'Invalid format file name %s' % self.format_file_name
        assert isinstance(self.videoType, str), 'Invalid meta type for video %s' % self.videoType

        SessionSupport.__init__(self)
        self._metaTypeId = None

    # ----------------------------------------------------------------
    def generateIdPath (self, id):
        path = "{0:03d}".format((id // 1000) % 1000)

        return path;

    # ----------------------------------------------------------------
    def deploy(self):
        '''
           Deploy
        '''
        self._thumbnailFormatGeneric = thumbnailFormatFor(self.session(), '%(size)s/video_generic.jpg')
        referenceLast = self.thumbnailManager.timestampThumbnail(self._thumbnailFormatGeneric.id)
        videoPath = join(pythonPath(), 'resources', 'other.jpg')
        if referenceLast is None or referenceLast < timestampURI(videoPath):
            self.thumbnailManager.processThumbnail(self._thumbnailFormatGeneric.id, videoPath)

        self._thumbnailFormat = thumbnailFormatFor(self.session(), '%(size)s/%(id)d.jpg')
        self._metaTypeId = metaTypeFor(self.session(), self.videoType).Id

    # ----------------------------------------------------------------
    def extractLength(self, line):
        #Duration: 00:00:30.06, start: 0.000000, bitrate: 585 kb/s
        property = line.partition(':')[2]
        property = property.partition(',')[0].strip()
        property = property.split(':')

        value = int(property[0]) * 60 + int(property[1]) * 60 + int(float(property[2]))

        return value

    # ----------------------------------------------------------------
    def extractVideo(self, line):
        #Stream #0.0(eng): Video: h264 (Constrained Baseline), yuv420p, 416x240, 518 kb/s, 29.97 fps, 29.97 tbr, 2997 tbn, 59.94 tbc
        properties = (line.rpartition('Video:')[2]).split(',')

        index = 0
        encoding = properties[index].strip()

        index += 2
        size = (properties[index].strip()).partition('x')
        width = int(size[0])
        height = int(size[2])

        index += 1
        bitrate = properties[index].strip().partition(' ')
        if bitrate[2] == 'kb/s':
            bitrate = int(float(bitrate[0]))
            index += 1
        else:
            bitrate = None

        fps = properties[index].strip().partition(' ')
        if fps[2] == 'fps':
            fps = int(float(fps[0]))
        else:
            fps = None

        return (encoding, width, height, bitrate, fps)

    # ----------------------------------------------------------------
    def extractAudio(self, line):
        #Stream #0.1(eng): Audio: aac, 44100 Hz, stereo, s16, 61 kb/s
        properties = (line.rpartition(':')[2]).split(',')

        index = 0
        encoding = properties[index].strip()

        index += 1
        sampleRate = properties[index].strip().partition(' ')
        if sampleRate[2] == 'Hz':
            sampleRate = int(float(sampleRate[0]))
        else:
            sampleRate = None

        index += 1
        channels = properties[index].strip()

        index += 2
        bitrate = properties[4].strip().partition(' ')
        if bitrate[2] == 'kb/s':
            bitrate = int(float(bitrate[0]))
        else:
            bitrate = None

        return (encoding, sampleRate, channels, bitrate)

    # ----------------------------------------------------------------
    def processByInfo(self, metaDataMapped, contentPath, contentType):
        if contentType != None and contentType.find(self.videoType) != -1:
            return self.process(metaDataMapped, contentPath)

        extension = metaDataMapped.Name.rpartition('.')[2]
        if self.video_supported_files.find(extension) != -1:
            return self.process(metaDataMapped, contentPath)

        return False

    # ----------------------------------------------------------------
    def process(self, metaDataMapped, contentPath):
        '''
        @see: IMetaDataHandler.process
        '''

        assert isinstance(metaDataMapped, MetaDataMapped), 'Invalid meta data mapped %s' % metaDataMapped

        thumbnailPath = contentPath + '.jpg'
        p = Popen(['avconv', '-i', contentPath, '-vframes', '1', '-an', '-ss', '2', thumbnailPath], stdin=PIPE, stdout=PIPE, stderr=STDOUT)
        if p.wait() != 0: return False

        if not exists(thumbnailPath): return False


        videoDataEntry = VideoDataEntry()
        videoDataEntry.Id = metaDataMapped.Id
        while 1:
            line = p.stdout.readline()
            if not line: break
            line = str(line, "utf-8")

            if line.find(': Video:') != -1:
                try:
                    values = self.extractVideo(line)
                    videoDataEntry.VideoEncoding = values[0]
                    videoDataEntry.Width = values[1]
                    videoDataEntry.Height = values[2]
                    videoDataEntry.VideoBitrate = values[3]
                    videoDataEntry.Fps = values[4]
                except: pass
            elif line.find(': Audio: ') != -1:
                try:
                    values = self.extractAudio(line)
                    videoDataEntry.AudioEncoding = values[0]
                    videoDataEntry.SampleRate = values[1]
                    videoDataEntry.Channels = values[2]
                    videoDataEntry.AudioBitrate = values[3]
                except: pass
            elif line.find('Duration: ') != -1:
                try: videoDataEntry.Length = self.extractLength(line)
                except: pass
            elif line.find('Output #0') != -1:
                break

        fileName = self.format_file_name % {'id': metaDataMapped.Id, 'file': metaDataMapped.Name}
        cdmPath = ''.join((self.videoType, '/', self.generateIdPath(metaDataMapped.Id), '/', fileName))

        metaDataMapped.content = cdmPath
        metaDataMapped.typeId = self._metaTypeId
        metaDataMapped.thumbnailFormatId = self._thumbnailFormat.id
        metaDataMapped.IsAvailable = True

        self.thumbnailManager.processThumbnail(self._thumbnailFormat.id, thumbnailPath, metaDataMapped)
        remove(thumbnailPath)

        try:
            self.session().add(videoDataEntry)
            self.session().flush((videoDataEntry,))
        except SQLAlchemyError as e:
            metaDataMapped.IsAvailable = False
            handle(e, VideoDataEntry)

        return True

