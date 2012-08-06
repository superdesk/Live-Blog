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
from superdesk.media_archive.core.spec import IThumbnailManager, \
    IThumbnailCreator
from cdm.spec import ICDM
from os.path import join, isfile
from ally.support.util_io import readGenerator
from shutil import copyfileobj

# --------------------------------------------------------------------

@injected
class ThumbnailManager(IThumbnailManager):
    '''
    Implementation for @see: IThumbnailManager
    '''
    thumbnailSizes = {}
    # dictionary containing thumbnail sizes
    # This is basically just a simple dictionary{string, tuple(integer, integer)} that has
    # as key a path safe name and as a value a tuple with the width/height of the thumbnail.
    # example: {'small': [100, 100]}
    thumbnailCreator = IThumbnailCreator
    # creates thumbnails based on the original image content and new size
    repositoryPath = str
    # path to the thumbnail repository
    cdm = ICDM
    # the content delivery manager where to publish thumbnails

    def processThumbnail(self, metadata, imagePath, size):
        '''
        @see IThumbnailManager.processThumbnail
        '''
        assert isinstance(metadata, MetaData), 'Invalid metadata %s' % metadata
        assert isinstance(imagePath, str) and isfile(imagePath), 'Invalid file path %s' % imagePath
        assert isinstance(size, str) and size in self.thumbnailSizes, 'Invalid size value %s' % size
        thumbPath = join(metadata.Type.Key, size, metadata.Name)
        thumbRepoPath = join(self.repositoryPath, thumbPath)
        if not isfile(thumbRepoPath):
            thContent = self.thumbnailCreator.createThumbnail(open(imagePath, 'rb'),
                                                              self.thumbnailSizes[size][0],
                                                              self.thumbnailSizes[size][0])
            with open(thumbRepoPath, 'wb') as thFile:
                copyfileobj(thContent, thFile)
            self.cdm.publishFromFile(thumbPath, thumbRepoPath)
        return readGenerator(open(thumbRepoPath, 'rb'))


class ThumbnailCreatorFFMpeg(IThumbnailCreator):
    '''
    Implementation for @see: IThumbnailCreator
    '''

    def createThumbnail(self, contentPath, width, height):
        #TODO: implement thumbnail creation
        return open(contentPath, 'rb')
