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
from os import remove
from os.path import exists, splitext, abspath
from ally.support.util_sys import pythonPath
from sqlalchemy.exc import SQLAlchemyError
from subprocess import Popen, PIPE, STDOUT
from superdesk.media_archive.core.impl.meta_service_base import \
    thumbnailFormatFor, metaTypeFor
from superdesk.media_archive.core.spec import IMetaDataHandler,\
    IThumbnailManager
import re
from os.path import join
from superdesk.media_archive.meta.meta_data import MetaDataMapped
from superdesk.media_archive.meta.video_data import META_TYPE_KEY,\
    VideoDataEntry

# --------------------------------------------------------------------

@injected
@setup(IMetaDataHandler, name='videoDataHandler')
class VideoPersistanceAlchemy(SessionSupport, IMetaDataHandler):
    '''
    Provides the service that handles the video persistence @see: IVideoPersistanceService.
    '''

    format_file_name = '%(id)s.%(file)s'; wire.config('format_file_name', doc='''
    The format for the videos file names in the media archive''')
    default_format_thumbnail = '%(size)s/video.jpg'; wire.config('default_format_thumbnail', doc='''
    The format for the video thumbnails in the media archive''')
    format_thumbnail = '%(size)s/%(id)s.%(name)s.jpg'; wire.config('format_thumbnail', doc='''
    The format for the video thumbnails in the media archive''')
    ffmpeg_path = join('workspace', 'tools', 'ffmpeg', 'bin', 'ffmpeg.exe'); wire.config('ffmpeg_path', doc='''
    The path where the ffmpeg is found''')

    video_supported_files = 'flv, avi, mov, mp4, mpg, wmv, 3gp, asf, rm, swf'

    thumbnailManager = IThumbnailManager; wire.entity('thumbnailManager')
    # Provides the thumbnail referencer

    def __init__(self):
        assert isinstance(self.format_file_name, str), 'Invalid format file name %s' % self.format_file_name
        assert isinstance(self.default_format_thumbnail, str), 'Invalid format thumbnail %s' % self.default_format_thumbnail
        assert isinstance(self.format_thumbnail, str), 'Invalid format thumbnail %s' % self.format_thumbnail
        assert isinstance(self.video_supported_files, str), 'Invalid supported files %s' % self.video_supported_files
        assert isinstance(self.ffmpeg_path, str), 'Invalid ffmpeg path %s' % self.ffmpeg_path
        assert isinstance(self.thumbnailManager, IThumbnailManager), 'Invalid thumbnail manager %s' % self.thumbnailManager

        self.videoSupportedFiles = set(re.split('[\\s]*\\,[\\s]*', self.video_supported_files))

    def deploy(self):
        '''
        @see: IMetaDataHandler.deploy
        '''
        
        self._defaultThumbnailFormat = thumbnailFormatFor(self.session(), self.default_format_thumbnail)
        self.thumbnailManager.putThumbnail(self._defaultThumbnailFormat.id, abspath(join(pythonPath(), 'resources', 'video.jpg')))
        
        self._thumbnailFormat = thumbnailFormatFor(self.session(), self.format_thumbnail)
        self._metaTypeId = metaTypeFor(self.session(), META_TYPE_KEY).Id

    def processByInfo(self, metaDataMapped, contentPath, contentType):
        '''
        @see: IMetaDataHandler.processByInfo
        '''
        if contentType is not None and contentType.startswith(META_TYPE_KEY):
            return self.process(metaDataMapped, contentPath)

        extension = splitext(metaDataMapped.Name)[1][1:]
        if extension in self.videoSupportedFiles: return self.process(metaDataMapped, contentPath)

        return False

    def process(self, metaDataMapped, contentPath):
        '''
        @see: IMetaDataHandler.process
        '''
        assert isinstance(metaDataMapped, MetaDataMapped), 'Invalid meta data mapped %s' % metaDataMapped

        thumbnailPath = contentPath + '.jpg'
        p = Popen((self.ffmpeg_path, '-i', contentPath, '-vframes', '1', '-an', '-ss', '2', thumbnailPath),
                  stdin=PIPE, stdout=PIPE, stderr=STDOUT)
        if p.wait() != 0: return False
        if not exists(thumbnailPath): return False

        videoDataEntry = VideoDataEntry()
        videoDataEntry.Id = metaDataMapped.Id
        while True:
            line = p.stdout.readline()
            if not line: break
            line = str(line, 'utf-8')

            if line.find('Video') != -1 and line.find('Stream') != -1:
                try:
                    values = self.extractVideo(line)
                    videoDataEntry.VideoEncoding = values[0]
                    videoDataEntry.Width = values[1]
                    videoDataEntry.Height = values[2]
                    if values[3]: videoDataEntry.VideoBitrate = values[3]
                    videoDataEntry.Fps = values[4]
                except: pass
            elif line.find('Audio') != -1 and line.find('Stream') != -1:
                try:
                    values = self.extractAudio(line)
                    videoDataEntry.AudioEncoding = values[0]
                    videoDataEntry.SampleRate = values[1]
                    videoDataEntry.Channels = values[2]
                    videoDataEntry.AudioBitrate = values[3]
                except: pass
            elif line.find('Duration') != -1 and line.find('start') != -1:
                try: 
                    values = self.extractDuration(line)
                    videoDataEntry.Length = values[0]
                    videoDataEntry.VideoBitrate = values[1]
                except: pass
            elif line.find('Output #0') != -1:
                break

        path = self.format_file_name % {'id': metaDataMapped.Id, 'file': metaDataMapped.Name}
        path = ''.join((META_TYPE_KEY, '/', self.generateIdPath(metaDataMapped.Id), '/', path))

        metaDataMapped.content = path
        metaDataMapped.typeId = self._metaTypeId
        metaDataMapped.thumbnailFormatId = self._thumbnailFormat.id
        metaDataMapped.IsAvailable = True

        self.thumbnailManager.putThumbnail(self._thumbnailFormat.id, thumbnailPath, metaDataMapped)
        remove(thumbnailPath)

        try:
            self.session().add(videoDataEntry)
            self.session().flush((videoDataEntry,))
        except SQLAlchemyError as e:
            metaDataMapped.IsAvailable = False
            handle(e, VideoDataEntry)

        return True

    # ----------------------------------------------------------------

    def extractDuration(self, line):
        #Duration: 00:00:30.06, start: 0.000000, bitrate: 585 kb/s
        properties = line.split(',')
        
        length = properties[0].partition(':')[2]
        length = length.strip().split(':')
        length = int(length[0]) * 60 + int(length[1]) * 60 + int(float(length[2]))

        bitrate = properties[2]
        bitrate = bitrate.partition(':')[2]
        bitrate = bitrate.strip().partition(' ')
        if bitrate[2] == 'kb/s':
            bitrate = int(float(bitrate[0]))
        else:
            bitrate = None

        return (length, bitrate)

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
        if fps[2] == 'fps' or fps[2] == 'tbr':
            fps = int(float(fps[0]))
        else:
            fps = None

        return (encoding, width, height, bitrate, fps)

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

    def generateIdPath (self, id):
        return "{0:03d}".format((id // 1000) % 1000)
