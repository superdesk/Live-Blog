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
from os.path import join, isfile, exists, isdir
from ally.support.util_io import readGenerator, timestampURI
from shutil import copyfileobj
from ally.exception import DevelError
from superdesk.media_archive.meta.meta_data import ThumbnailFormat
from ally.container import wire
from ally.support.sqlalchemy.session import SessionSupport
from os import makedirs, access, W_OK
from collections import OrderedDict

# --------------------------------------------------------------------

ORIGINAL_SIZE = 'original'
# Provides the size name for the original sized images from which the thumbnails are created

# --------------------------------------------------------------------

@injected
class ThumbnailManager(SessionSupport, IThumbnailManager):
    '''
    Implementation for @see: IThumbnailManager
    '''
    thumbnail_dir_path = join('workspace', 'media_archive', 'process_thumbnail'); wire.config('thumbnail_dir_path', doc='''
    The folder path where the thumbnail images are placed for resizing''')
    # path to the thumbnail repository

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
        thumbnailSizes = [(key, sizes) for key, sizes in self.thumbnailSizes.items()]
        thumbnailSizes.sort(key=lambda pack: pack[1][0] * pack[1][1])
        self.thumbnailSizes = OrderedDict(thumbnailSizes)
        self._cache_thumbnail = {}

    def processThumbnail(self, metadata, imagePath, size, scheme):
        '''
        @see IThumbnailManager.processThumbnail
        '''
        assert isinstance(metadata, MetaData), 'Invalid metadata %s' % metadata
        assert isinstance(imagePath, str) and isfile(imagePath), 'Invalid file path %s' % imagePath
        assert isinstance(size, str) and size in self.thumbnailSizes, 'Invalid size value %s' % size

        if not metadata.thumbnailFormatId:
            return metadata

        keys = {'id': metadata.Id, 'name': metadata.Name}
        if size:
            assert isinstance(size, str), 'Invalid thumb size %s' % size
            if size not in self.thumbnailSizes: raise DevelError('Unknown thumbnail size %s' % size)
            keys['size'] = size
        elif self.thumbnailSizes:
            keys['size'] = next(iter(self.thumbnailSizes))
        else:
            keys['size'] = ORIGINAL_SIZE
        thumbPath = self._getFormat(metadata.thumbnailFormatId) % keys
        thumbTimestamp = self.timestampThumbnail(metadata.thumbnailFormatId, metadata.Id, metadata.Name)
        if not thumbTimestamp or thumbTimestamp < timestampURI(imagePath):
            thContent = self.thumbnailCreator.createThumbnail(open(imagePath, 'rb'),
                                                              self.thumbnailSizes[size][0],
                                                              self.thumbnailSizes[size][0])
            thumbRepoPath = join(self.thumbnail_dir_path, thumbPath)
            with open(thumbRepoPath, 'wb') as thFile:
                copyfileobj(thContent, thFile)
            self.cdm.publishFromFile(thumbPath, thumbRepoPath)
        metadata.Thumbnail = self.cdm.getURI(thumbPath, scheme)
        return metadata

    def timestampThumbnail(self, thumbnailId, metaDataId=None, metaDataName=None):
        '''
        @see: IThumbnailReferencer.timestampThumbnail
        '''
        try:
            return self.cdm.getTimestamp(self._reference(thumbnailId, metaDataId, metaDataName))
        except PathNotFound:
            return None

    # ----------------------------------------------------------------

    def _getFormat(self, thumbnailFormatId):
        '''
        Provides the format for the thumbnail id
        '''
        format = self._cache_thumbnail.get(thumbnailFormatId)
        if format is None:
            thumbnail = self.session().query(ThumbnailFormat).get(thumbnailFormatId)
            assert isinstance(thumbnail, ThumbnailFormat), 'Invalid thumbnail %s' % thumbnail
            format = self._cache_thumbnail[thumbnail.id] = thumbnail.format
        return format

    def _reference(self, thumbnailFormatId, metaDataId=None, metaDataName=None):
        '''
        Construct the reference based on the provided parameters.
        '''
        assert isinstance(thumbnailFormatId, int), 'Invalid thumbnail id %s' % thumbnailFormatId
        keys = {'size': ORIGINAL_SIZE}
        if metaDataId:
            assert isinstance(metaDataId, int), 'Invalid meta data id %s' % metaDataId
            keys['id'] = metaDataId
        if metaDataName:
            assert isinstance(metaDataName, str), 'Invalid meta data name %s' % metaDataName
            keys['name'] = metaDataName

        return self._getFormat(thumbnailFormatId) % keys

class ThumbnailCreatorFFMpeg(IThumbnailCreator):
    '''
    Implementation for @see: IThumbnailCreator
    '''

    def createThumbnail(self, contentPath, width, height):
        #TODO: implement thumbnail creation
        return open(contentPath, 'rb')
