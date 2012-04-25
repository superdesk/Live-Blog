'''
Created on Apr 25, 2012

@package: superdesk media archive
@copyright: 2012 Sourcefabric o.p.s.
@license: http://www.gnu.org/licenses/gpl-3.0.txt
@author: Gabriel Nistor

Implementation for the image persistence API.
'''

from ..api.image_persist import IImagePersistanceService
from .meta_data import IMetaDataReferenceHandler
from ally.container import wire
from ally.container.ioc import injected
from collections import OrderedDict
from genericpath import isdir
from os.path import join
import os
from superdesk.media_archive.meta.meta_data import MetaData
from superdesk.media_archive.api import image_info as api
from cdm.spec import ICDM
from ally.api.model import Content
from superdesk.media_archive.meta.image_info import ImageInfo
from ally.support.api.util_service import namesForModel
from ally.support.sqlalchemy.util_service import handle
from sqlalchemy.exc import SQLAlchemyError
from ally.support.sqlalchemy.session import SessionSupport

# --------------------------------------------------------------------

@injected
class ImagePersistanceService(IImagePersistanceService, IMetaDataReferenceHandler, SessionSupport):
    '''
    Provides the service that handles the @see: IImagePersistanceService.
    '''

    image_dir_path = join('workspace', 'media_archive', 'image_queue'); wire.config('image_dir_path', doc='''
    The folder path where the images are queued for processing''')

    thumbnailSizes = dict
    # Contains the thumbnail sizes available for the media archive.
    # This is basically just a simple dictionary{string, tuple(integer, integer)} that has as a key a path safe name
    # and as a value a tuple with the width/height of the thumbnail.

    cdmImages = ICDM
    cdmThumbnails = ICDM

    def __init__(self):
        assert isinstance(self.image_dir_path, str), 'Invalid image directory %s' % self.image_dir_path
        assert isinstance(self.thumbnailSizes, dict), 'Invalid thumbnail sizes %s' % self.thumbnailSizes
        assert isinstance(self.cdmImages, ICDM), 'Invalid image CDM %s' % self.cdmImages
        assert isinstance(self.cdmThumbnails, ICDM), 'Invalid image thumbnail CDM %s' % self.cdmThumbnails
        SessionSupport.__init__(self)

        if not os.path.exists(self.image_dir_path): os.makedirs(self.image_dir_path)
        if not isdir(self.image_dir_path) or not os.access(self.image_dir_path, os.W_OK):
            raise IOError('Unable to access the repository directory %s' % self.image_dir_path)

        # We order the thumbnail sizes in descending order
        thumbnailSizes = [(key, sizes) for key, sizes in self.thumbnailSizes.items()]
        thumbnailSizes.sort(key=lambda pack: pack[1][0] * pack[1][1])
        self.thumbnailSizes = OrderedDict(thumbnailSizes)

    def insert(self, imageInfo, image):
        '''
        @see: IImagePersistanceService.insert
        '''
        assert isinstance(imageInfo, api.ImageInfo), 'Invalid image info %s' % imageInfo
        assert isinstance(image, Content), 'Invalid image content %s' % image

        imageInfoDb = ImageInfo()
        for prop in namesForModel(imageInfo):
            if getattr(ImageInfo, prop) in imageInfo: setattr(imageInfoDb, prop, getattr(imageInfo, prop))
        try:
            self.session().add(imageInfoDb)
            self.session().flush((imageInfoDb,))
        except SQLAlchemyError as e: handle(e, imageInfoDb)
        #TODO: continue implementation
        return imageInfoDb.Id

    # ----------------------------------------------------------------

    def process(self, metaData, thumbSize):
        '''
        @see: IMetaDataReferenceHandler.process
        '''
        assert isinstance(metaData, MetaData), 'Invalid meta data %s' % metaData
        metaData.IsAvailable = False
        return metaData

