'''
Created on Apr 27, 2012

@package: superdesk media archive
@copyright: 2012 Sourcefabric o.p.s.
@license: http://www.gnu.org/licenses/gpl-3.0.txt
@author: Gabriel Nistor

Provides the specification classes for the media archive.
'''

import abc

# --------------------------------------------------------------------

class IMetaDataReferencer(metaclass=abc.ABCMeta):
    '''
    Provides the meta data references handler.
    '''

    @abc.abstractclassmethod
    def populate(self, metaData, scheme, thumbSize=None):
        '''
        Processes the meta data references in respect with the specified thumbnail size. The method will take no action if
        the meta data is not relevant for the handler.

        @param metaData: MetaDataMapped (from the meta package)
            The meta data to have the references processed.
        @param scheme: string
            The scheme protocol to provide the references for.
        @param thumbSize: string|None
            The thumbnail size to process for the reference, None value lets the handler peek the thumbnail size.
        @return: MetaData
            The populated meta data, usually the same meta data.
        '''

class IMetaDataHandler(metaclass=abc.ABCMeta):
    '''
    Interface that provides the handling for the meta data's.
    '''

    @abc.abstractclassmethod
    def deploy(self):
        '''
        Deploy the handler, at this moment the handler should create the required meta types and thumbnail specifications.
        '''

    @abc.abstractclassmethod
    def process(self, metaData, contentPath):
        '''
        Processes the meta data persistence and type association. The meta data will already be in the database this method
        has to update associate the meta data in respect with the handler. The method will take no action if the content is
        not relevant for the handler.

        @param metaData: MetaDataMapped
            The mapped meta data for the current uploaded content.
        @param contentPath: string
            The content local file system path where the content can be found.
        @return: boolean
            True if the content has been processed, False otherwise.
        '''

class IThumbnailManager(IMetaDataReferencer):
    '''
    Interface that defines the API for handling thumbnails.
    '''

    def processThumbnail(self, thumbnailFormatId, imagePath, size, metaData=None):
        '''
        Process a file identified by metaData.
        Return the thumbnail content for the given metaData.

        @param thumbnailFormatId: int
            The thumbnail path format identifier
        @param imagePath: str
            The path to the original image from which to generate the thumbnail.
        @param size: str
            The size identifier
        @param metaData: Metadata
            The object containing the content metadata for which the thumbnail is generated.
        '''

    @abc.abstractclassmethod
    def timestampThumbnail(self, thumbnailFormatId, metaData=None):
        '''
        Provides the thumbnail last modification time stamp.

        @param thumbnailFormatId: integer
            The thumbnail format id to process the timestamp for.
        @param metaData: Metadata
            The object containing the content metadata for which the thumbnail was generated.
        @return: datetime|None
            The datetime of the last modification or None if there is no resource for the thumbnail path.
        '''

class IThumbnailCreator(metaclass=abc.ABCMeta):
    '''
    Specification class that provides the thumbnail creation.
    '''

    @abc.abstractclassmethod
    def createThumbnail(self, contentPath, width, height):
        '''
        Create a thumbnail for the provided content.

        @param contentPath: string
            The content local file system path where the original content can be found.
        @param width: integer
            The thumbnail width.
        @param height: integer
            The thumbnail height.
        @return: file bytes object
            The file like object that is the thumbnail.
        '''
