'''
Created on Apr 27, 2012

@package: superdesk media archive
@copyright: 2012 Sourcefabric o.p.s.
@license: http://www.gnu.org/licenses/gpl-3.0.txt
@author: Gabriel Nistor

Provides the thumbnail referencer implementation.
'''

from ..spec import IThumbnailReferencer
from ally.container.ioc import injected
from ally.exception import DevelError
from ally.support.sqlalchemy.session import SessionSupport
from cdm.spec import ICDM, PathNotFound
from collections import OrderedDict
from superdesk.media_archive.meta.meta_data import MetaDataMapped, Thumbnail
from genericpath import isfile
from ally.container import wire
from os import makedirs, access, W_OK
from os.path import join, exists, isdir
from ally.support.util_io import pipe

# --------------------------------------------------------------------

ORIGINAL_SIZE = 'original'
# Provides the size name for the original sized images from which the thumbnails are created

# --------------------------------------------------------------------

@injected
class ThumbnailReferencer(SessionSupport, IThumbnailReferencer):
    '''
    Provides a basic implementation for @see: IThumbnailReferencer
    '''

    thumbnail_dir_path = join('workspace', 'media_archive', 'process_thumbnail'); wire.config('thumbnail_dir_path', doc='''
    The folder path where the thumbnail images are placed for resizing''')

    thumbnailSizes = dict
    # Contains the thumbnail sizes available for the media archive.
    # This is basically just a simple dictionary{string, tuple(integer, integer)} that has as a key a path safe name
    # and as a value a tuple with the width/height of the thumbnail.
    cdmThumbnail = ICDM
    # The thumbnail CDM.

    def __init__(self):
        assert isinstance(self.thumbnail_dir_path, str), 'Invalid processing directory %s' % self.thumbnail_dir_path
        assert isinstance(self.thumbnailSizes, dict), 'Invalid thumbnail sizes %s' % self.thumbnailSizes
        assert isinstance(self.cdmThumbnail, ICDM), 'Invalid thumbnail CDM %s' % self.cdmThumbnail
        SessionSupport.__init__(self)

        if not exists(self.thumbnail_dir_path): makedirs(self.thumbnail_dir_path)
        if not isdir(self.thumbnail_dir_path) or not access(self.thumbnail_dir_path, W_OK):
            raise IOError('Unable to access the processing directory %s' % self.thumbnail_dir_path)

        # We order the thumbnail sizes in descending order
        thumbnailSizes = [(key, sizes) for key, sizes in self.thumbnailSizes.items()]
        thumbnailSizes.sort(key=lambda pack: pack[1][0] * pack[1][1])
        self.thumbnailSizes = OrderedDict(thumbnailSizes)
        self._cache_thumbnail = {}

    def populate(self, metaData, scheme, thumbSize=None):
        '''
        @see: IThumbnailReferencer.populate
        '''
        assert isinstance(metaData, MetaDataMapped), 'Invalid meta data %s' % metaData
        if metaData.thumbnailId:
            keys = {'id': metaData.Id, 'name': metaData.Name}
            if thumbSize:
                assert isinstance(thumbSize, str), 'Invalid thumb size %s' % thumbSize
                if thumbSize not in self.thumbnailSizes: raise DevelError('Unknown thumbnail size %s' % thumbSize)
                keys['size'] = thumbSize
            elif self.thumbnailSizes:
                keys['size'] = next(iter(self.thumbnailSizes))
            else:
                keys['size'] = ORIGINAL_SIZE
            metaData.Thumbnail = self.cdmThumbnail.getURI(self._getFormat(metaData.thumbnailId) % keys, scheme)
        return metaData

    def processThumbnail(self, image, thumbnailId, metaDataId=None, metaDataName=None):
        '''
        @see: IThumbnailReferencer.processThumbnail
        '''
        path = self._reference(thumbnailId, metaDataId, metaDataName)
        if isinstance(image, str):
            # The image must be a file system path.
            assert isfile(image), 'Invalid image path %s' % image
            imagePath = image
        else:
            # The image must be a file object
            with image:
                imagePath = join(self.thumbnail_dir_path, path.split('/')[-1])
                with open(imagePath, 'w+b') as fobj: pipe(image, fobj)

        with open(imagePath, 'rb') as fobj: self.cdmThumbnail.publishFromFile(path, fobj)

        #TODO: add resizing then delete files

    def timestampThumbnail(self, thumbnailId, metaDataId=None, metaDataName=None):
        '''
        @see: IThumbnailReferencer.timestampThumbnail
        '''
        try:
            return self.cdmThumbnail.getTimestamp(self._reference(thumbnailId, metaDataId, metaDataName))
        except PathNotFound:
            return None

    # ----------------------------------------------------------------

    def _getFormat(self, thumbnailId):
        '''
        Provides the format for the thumbnail id
        '''
        format = self._cache_thumbnail.get(thumbnailId)
        if format is None:
            thumbnail = self.session().query(Thumbnail).get(thumbnailId)
            assert isinstance(thumbnail, Thumbnail), 'Invalid thumbnail %s' % thumbnail
            format = self._cache_thumbnail[thumbnail.id] = thumbnail.format
        return format

    def _reference(self, thumbnailId, metaDataId=None, metaDataName=None):
        '''
        Construct the reference based on the provided parameters.
        '''
        assert isinstance(thumbnailId, int), 'Invalid thumbnail id %s' % thumbnailId
        keys = {'size': ORIGINAL_SIZE}
        if metaDataId:
            assert isinstance(metaDataId, int), 'Invalid meta data id %s' % metaDataId
            keys['id'] = metaDataId
        if metaDataName:
            assert isinstance(metaDataName, str), 'Invalid meta data name %s' % metaDataName
            keys['name'] = metaDataName

        return self._getFormat(thumbnailId) % keys
