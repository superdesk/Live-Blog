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
from ally.support.sqlalchemy.session import SessionSupport
from superdesk.media_archive.meta.meta_data import MetaDataMapped
from genericpath import isfile
from ally.support.util_io import pipe
from superdesk.media_archive.core.spec import IThumbnailManager

# --------------------------------------------------------------------

@injected
class ThumbnailReferencer(SessionSupport, IThumbnailReferencer):
    '''
    Provides a basic implementation for @see: IThumbnailReferencer
    '''
    thumbnailManager = IThumbnailManager

    def __init__(self):
        assert isinstance(self.thumbnailManager, IThumbnailManager), 'Invalid thumbnail manager %s' % self.thumbnailManager
        SessionSupport.__init__(self)

    def populate(self, metadata, scheme, size=None):
        '''
        @see: IThumbnailReferencer.populate
        '''
        assert isinstance(metadata, MetaDataMapped), 'Invalid meta data %s' % metadata
        return self.thumbnailManager.processThumbnail(metadata, 'imagePath', size, scheme)

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
