'''
Created on Aug 3, 2012

@package: internationalization
@copyright: 2012 Sourcefabric o.p.s.
@license: http://www.gnu.org/licenses/gpl-3.0.txt
@author: Mugur Rus

Thumbnail manager class definition.
'''
# --------------------------------------------------------------------

from ally.container.ioc import injected
from superdesk.media_archive.api.meta_data import MetaData
from superdesk.media_archive.core.spec import IThumbnailManager, IThumbnailCreator
from cdm.spec import ICDM, PathNotFound
from os.path import join, isfile, exists, isdir, dirname
from ally.support.util_io import timestampURI
from ally.container.support import setup
from shutil import copyfile
from ally.exception import DevelError
from superdesk.media_archive.meta.meta_data import ThumbnailFormat
from ally.container import wire
from ally.support.sqlalchemy.session import SessionSupport
from os import access, W_OK, makedirs
from collections import OrderedDict
from subprocess import Popen
from ally.zip.util_zip import normOSPath

# --------------------------------------------------------------------

ORIGINAL_SIZE = 'original'
# Provides the size name for the original sized images from which the thumbnails are created

# --------------------------------------------------------------------

@injected
@setup(IThumbnailManager)
class ThumbnailManager(SessionSupport, IThumbnailManager):
    '''
    Implementation for @see: IThumbnailManager
    '''
    thumbnail_dir_path = join('workspace', 'media_archive', 'process_thumbnail'); wire.config('thumbnail_dir_path', doc='''
    The folder path where the thumbnail images are placed for resizing''')
    # path to the thumbnail repository
    original_width = 512; wire.config('original_width', doc='''
    The width of the original thumbnail from which other sizes are generated''')
    original_height = 512; wire.config('original_height', doc='''
    The width of the original thumbnail from which other sizes are generated''')

    thumbnailSizes = {}
    # dictionary containing thumbnail sizes
    # This is basically just a simple dictionary{string, tuple(integer, integer)} that has
    # as key a path safe name and as a value a tuple with the width/height of the thumbnail.
    # example: {'small': [100, 100]}
    thumbnailCreator = IThumbnailCreator
    # object that does the actual thumbnail generation from the original image
    cdm = ICDM
    # the content delivery manager where to publish thumbnails

    def __init__(self):
        assert isinstance(self.thumbnail_dir_path, str), 'Invalid processing directory %s' % self.thumbnail_dir_path
        assert isinstance(self.thumbnailSizes, dict), 'Invalid thumbnail sizes %s' % self.thumbnailSizes
        assert isinstance(self.thumbnailCreator, IThumbnailCreator), 'Invalid thumbnail creator %s' % self.thumbnailCreator
        assert isinstance(self.cdm, ICDM), 'Invalid thumbnail CDM %s' % self.cdm

        if not exists(self.thumbnail_dir_path): makedirs(self.thumbnail_dir_path)
        if not isdir(self.thumbnail_dir_path) or not access(self.thumbnail_dir_path, W_OK):
            raise IOError('Unable to access the processing directory %s' % self.thumbnail_dir_path)

        SessionSupport.__init__(self)
        # We order the thumbnail sizes in descending order
        self.thumbnailSizes[ORIGINAL_SIZE] = [self.original_width, self.original_height]
        thumbnailSizes = [(key, sizes) for key, sizes in self.thumbnailSizes.items()]
        thumbnailSizes.sort(key=lambda pack: pack[1][0] * pack[1][1])
        self.thumbnailSizes = OrderedDict(thumbnailSizes)
        self._cache_thumbnail = {}

    def populate(self, metaData, scheme, thumbSize=None):
        assert isinstance(metaData, MetaData), 'Invalid metaData %s' % metaData
        thumbSize = thumbSize if thumbSize else ORIGINAL_SIZE
        assert isinstance(thumbSize, str) and thumbSize in self.thumbnailSizes, \
        'Invalid size value %s' % thumbSize

        if not metaData.thumbnailFormatId:
            return metaData
        thumbPath = self._reference(metaData.thumbnailFormatId, metaData.Id, metaData.Name, thumbSize)
        try: self.cdm.getTimestamp(thumbPath)
        except PathNotFound:
            if thumbSize == ORIGINAL_SIZE: raise DevelError('Unable to find a thumbnail for %s' % scheme)
            originalImagePath = self._reference(metaData.thumbnailFormatId, metaData.Id, metaData.Name)
            self.processThumbnail(metaData.thumbnailFormatId, originalImagePath, metaData, thumbSize)
        metaData.Thumbnail = self.cdm.getURI(thumbPath, scheme)
        return metaData

    def processThumbnail(self, thumbnailFormatId, imagePath, metaData=None, size=None):
        '''
        @see IThumbnailManager.processThumbnail
        '''
        assert isinstance(thumbnailFormatId, int), \
        'Invalid thumbnail format identifier %s' % thumbnailFormatId
        assert isinstance(imagePath, str) and isfile(imagePath), 'Invalid file path %s' % imagePath
        assert not metaData or isinstance(metaData, MetaData), 'Invalid metaData %s' % metaData
        size = size if size else ORIGINAL_SIZE
        assert isinstance(size, str) and size in self.thumbnailSizes, \
        'Invalid size value %s' % size

        (metaDataId, metaDataName) = (None, None) if not metaData else (metaData.Id, metaData.Name)
        thumbPath = self._reference(thumbnailFormatId, metaDataId, metaDataName, size)
        thumbTimestamp = self.timestampThumbnail(thumbnailFormatId, metaData, size)
        if not thumbTimestamp or thumbTimestamp < timestampURI(imagePath):
            thumbRepoPath = normOSPath(join(self.thumbnail_dir_path, thumbPath))
            if not isdir(dirname(thumbRepoPath)): makedirs(dirname(thumbRepoPath))
            copyfile(imagePath, thumbRepoPath)
            self.thumbnailCreator.createThumbnail(thumbRepoPath,
                                                  self.thumbnailSizes[size][0],
                                                  self.thumbnailSizes[size][0])
            self.cdm.publishFromFile(thumbPath, thumbRepoPath)

    def timestampThumbnail(self, thumbnailFormatId, metaData=None, size=None):
        '''
        @see: IThumbnailManager.timestampThumbnail
        '''
        assert isinstance(thumbnailFormatId, int), \
        'Invalid thumbnail format identifier %s' % thumbnailFormatId
        assert not metaData or isinstance(metaData, MetaData), 'Invalid metaData %s' % metaData
        size = size if size else ORIGINAL_SIZE
        assert isinstance(size, str) and size in self.thumbnailSizes, \
        'Invalid size value %s' % size

        if not metaData: metaDataId, metaDataName = None, None
        else: metaDataId, metaDataName = metaData.Id, metaData.Name
        try:
            return self.cdm.getTimestamp(self._reference(thumbnailFormatId, metaDataId, metaDataName, size))
        except PathNotFound:
            return None

    # ----------------------------------------------------------------

    def _getFormat(self, thumbnailFormatId):
        '''
        Provides the format for the thumbnail id
        '''
        format = self._cache_thumbnail.get(thumbnailFormatId)
        if format is None:
            thumbnailFormat = self.session().query(ThumbnailFormat).get(thumbnailFormatId)
            assert isinstance(thumbnailFormat, ThumbnailFormat), 'Invalid thumbnail %s' % thumbnailFormat
            format = self._cache_thumbnail[thumbnailFormat.id] = thumbnailFormat.format
        return format

    def _reference(self, thumbnailFormatId, metaDataId=None, metaDataName=None, size=ORIGINAL_SIZE):
        '''
        Construct the reference based on the provided parameters.
        '''
        keys = {'size': size}
        if metaDataId:
            assert isinstance(metaDataId, int), 'Invalid meta data id %s' % metaDataId
            keys['id'] = metaDataId
        if metaDataName:
            assert isinstance(metaDataName, str), 'Invalid meta data name %s' % metaDataName
            keys['name'] = metaDataName

        return self._getFormat(thumbnailFormatId) % keys


class ThumbnailCreatorGraphicsMagick(IThumbnailCreator):
    '''
    Implementation for @see: IThumbnailCreator
    '''
    graphics_magick_command = 'gm'; wire.config('graphics_magick_command', doc='''The format of the graphics magic comand''')

    def __init__(self):
        assert isinstance(self.graphics_magick_command, str), 'Invalid graphics magic command %s' % self.graphics_magick_command

    def createThumbnail(self, contentPath, width, height):
        thSize = str(width) + 'x' + str(height)
        Popen([self.graphics_magick_command, 'mogrify', '-resize', thSize, contentPath])
        return open(contentPath, 'rb')
