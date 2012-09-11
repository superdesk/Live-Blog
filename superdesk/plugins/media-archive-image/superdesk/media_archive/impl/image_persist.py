'''
Created on Apr 25, 2012

@package: superdesk media archive
@copyright: 2012 Sourcefabric o.p.s.
@license: http://www.gnu.org/licenses/gpl-3.0.txt
@author: Gabriel Nistor

Implementation for the image persistence API.
'''

from ..core.spec import IThumbnailManager
from ..meta.image_data import ImageDataEntry
from ..meta.meta_data import MetaDataMapped
from ally.container import wire
from ally.container.ioc import injected
from ally.container.support import setup
from ally.support.sqlalchemy.session import SessionSupport
from ally.support.sqlalchemy.util_service import handle
from datetime import datetime
from os.path import join
from sqlalchemy.exc import SQLAlchemyError
from superdesk.media_archive.core.impl.meta_service_base import \
    thumbnailFormatFor, metaTypeFor
from superdesk.media_archive.core.spec import IMetaDataHandler
from superdesk.media_archive.meta.image_data import META_TYPE_KEY
import re
import subprocess
from ntpath import splitext

# --------------------------------------------------------------------

@injected
@setup(IMetaDataHandler, 'imageDataHandler')
class ImagePersistanceAlchemy(SessionSupport, IMetaDataHandler):
    '''
    Provides the service that handles the image persistence @see: IImagePersistanceService.
    '''

    format_file_name = '%(id)s.%(file)s'; wire.config('format_file_name', doc='''
    The format for the images file names in the media archive''')
    format_thumbnail = '%(size)s/%(id)s.%(name)s.jpg'; wire.config('format_thumbnail', doc='''
    The format for the images thumbnails in the media archive''')
    image_supported_files = 'gif, png, bmp, jpg';wire.config('image_supported_files', doc='''
    The image formats supported by media archive image plugin''')

    thumbnailManager = IThumbnailManager; wire.entity('thumbnailManager')
    # Provides the thumbnail referencer

    def __init__(self):
        assert isinstance(self.format_file_name, str), 'Invalid format file name %s' % self.format_file_name
        assert isinstance(self.format_thumbnail, str), 'Invalid format thumbnail %s' % self.format_thumbnail
        assert isinstance(self.image_supported_files, str), 'Invalid supported files %s' % self.image_supported_files
        assert isinstance(self.thumbnailManager, IThumbnailManager), 'Invalid thumbnail manager %s' % self.thumbnailManager
        SessionSupport.__init__(self)

        self.imageSupportedFiles = set(re.split('[\\s]*\\,[\\s]*', self.image_supported_files))

    def deploy(self):
        '''
        @see: IMetaDataHandler.deploy
        '''
        self._thumbnailFormat = thumbnailFormatFor(self.session(), self.format_thumbnail)
        self._metaTypeId = metaTypeFor(self.session(), META_TYPE_KEY).Id

    def processByInfo(self, metaDataMapped, contentPath, contentType):
        '''
        @see: IMetaDataHandler.processByInfo
        '''
        if contentType is not None and contentType.find(META_TYPE_KEY) > 0:
            return self.process(metaDataMapped, contentPath)

        extension = splitext(metaDataMapped.Name)[1][1:]
        if extension in self.imageSupportedFiles: return self.process(metaDataMapped, contentPath)

        return False

    def process(self, metaDataMapped, contentPath):
        '''
        @see: IMetaDataHandler.process
        '''
        assert isinstance(metaDataMapped, MetaDataMapped), 'Invalid meta data mapped %s' % metaDataMapped

        jarPath = join('tools', 'media-archive-image', 'metadata_extractor.jar');
        p = subprocess.Popen(['java', '-jar', jarPath, contentPath],
                             stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
        if p.wait() != 0: return False

        imageDataEntry = ImageDataEntry()
        imageDataEntry.Id = metaDataMapped.Id
        while True:
            line = p.stdout.readline()
            if not line: break
            line = str(line, "utf-8")

            if line.find('] Image Width -') != -1:
                imageDataEntry.Width = self.extractNumber(line)
            elif line.find('] Image Height -') != -1:
                imageDataEntry.Height = self.extractNumber(line)
            elif line.find('] Date/Time Original -') != -1:
                imageDataEntry.CreationDate = self.extractDateTime(line)
            elif line.find('] Make -') != -1:
                imageDataEntry.CameraMake = self.extractString(line)
            elif line.find('] Model -') != -1:
                imageDataEntry.CameraModel = self.extractString(line)


        path = self.format_file_name % {'id': metaDataMapped.Id, 'file': metaDataMapped.Name}
        path = ''.join((META_TYPE_KEY, '/', self.generateIdPath(metaDataMapped.Id), '/', path))

        metaDataMapped.content = path
        metaDataMapped.typeId = self._metaTypeId
        metaDataMapped.thumbnailFormatId = self._thumbnailFormat.id
        metaDataMapped.IsAvailable = True

        self.thumbnailManager.putThumbnail(self._thumbnailFormat.id, contentPath, metaDataMapped)

        try: self.session().add(imageDataEntry)
        except SQLAlchemyError as e:
            metaDataMapped.IsAvailable = False
            handle(e, ImageDataEntry)

        return True

    # ----------------------------------------------------------------

    def extractNumber(self, line):
        for s in line.split():
            if s.isdigit():
                return int(s)

    def extractString(self, line):
        str = line.partition('-')[2].strip('\n')
        return str

    def extractDateTime(self, line):
        #example:' 2010:11:08 18:33:13'
        dateTimeFormat = ' %Y:%m:%d %H:%M:%S'
        str = line.partition('-')[2].strip('\n')
        return datetime.strptime(str, dateTimeFormat)

    # ----------------------------------------------------------------

    def generateIdPath (self, id):
        return "{0:03d}".format((id // 1000) % 1000)


