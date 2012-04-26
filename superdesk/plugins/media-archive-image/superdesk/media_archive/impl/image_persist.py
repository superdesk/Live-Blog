'''
Created on Apr 25, 2012

@package: superdesk media archive
@copyright: 2012 Sourcefabric o.p.s.
@license: http://www.gnu.org/licenses/gpl-3.0.txt
@author: Gabriel Nistor

Implementation for the image persistence API.
'''

from ..api import image_info as api
from ..api.image_persist import IImagePersistanceService
from ..meta.image_data import ImageData
from ..meta.image_info import ImageInfo
from ..meta.meta_data import MetaDataMapped
from ..meta.meta_type import MetaTypeMapped
from .meta_data import IMetaDataReferenceHandler
from ally.api.model import Content
from ally.container import wire
from ally.container.ioc import injected
from ally.support.api.util_service import namesForModel
from ally.support.sqlalchemy.session import SessionSupport
from ally.support.sqlalchemy.util_service import handle
from ally.support.util_io import pipe
from cdm.spec import ICDM, PathNotFound
from collections import OrderedDict
from datetime import datetime
from genericpath import isdir
from os.path import join, getsize
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm.exc import NoResultFound
import os

# --------------------------------------------------------------------

@injected
class ImagePersistanceService(IImagePersistanceService, IMetaDataReferenceHandler, SessionSupport):
    '''
    Provides the service that handles the @see: IImagePersistanceService.
    '''

    image_dir_path = join('workspace', 'media_archive', 'image_queue'); wire.config('image_dir_path', doc='''
    The folder path where the images are queued for processing''')
    format_file_name = '%(id)s.%(file)s'; wire.config('format_file_name', doc='''
    The format for the images file names in the media archive''')
    default_file_name = 'unknown'; wire.config('default_file_name', doc='''
    The default file name if non is specified''')

    imageTypeName = 'image'
    # The name for the meta type image

    thumbnailSizes = dict
    # Contains the thumbnail sizes available for the media archive.
    # This is basically just a simple dictionary{string, tuple(integer, integer)} that has as a key a path safe name
    # and as a value a tuple with the width/height of the thumbnail.

    cdmImages = ICDM
    cdmThumbnails = ICDM

    def __init__(self):
        assert isinstance(self.image_dir_path, str), 'Invalid image directory %s' % self.image_dir_path
        assert isinstance(self.format_file_name, str), 'Invalid format file name %s' % self.format_file_name
        assert isinstance(self.default_file_name, str), 'Invalid default file name %s' % self.default_file_name
        assert isinstance(self.imageTypeName, str), 'Invalid meta type image name %s' % self.imageTypeName
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

        self._metaTypeId = None

    def insert(self, imageInfo, image):
        '''
        @see: IImagePersistanceService.insert
        '''
        assert isinstance(imageInfo, api.ImageInfo), 'Invalid image info %s' % imageInfo
        assert isinstance(image, Content), 'Invalid image content %s' % image

        imageData = ImageData()
        imageData.CreatedOn = datetime.now()
        imageData.typeId = self._typeId()

        try:
            self.session().add(imageData)
            self.session().flush((imageData,))

            reference = self.format_file_name % {'id': imageData.Id, 'file': image.getName() or self.default_file_name}
            path = join(self.image_dir_path, reference)
            with open(path, 'wb') as fobj: pipe(image, fobj)

            assert isinstance(imageData, MetaDataMapped)
            imageData.reference = reference
            imageData.SizeInBytes = getsize(path)
            imageData.Width = 100
            imageData.Height = 100

            self.session().flush((imageData,))

            imageInfoDb = ImageInfo()
            for prop in namesForModel(imageInfo):
                if getattr(ImageInfo, prop) in imageInfo: setattr(imageInfoDb, prop, getattr(imageInfo, prop))
            imageInfoDb.MetaData = imageData.Id

            self.session().add(imageInfoDb)
            self.session().flush((imageInfoDb,))
        except SQLAlchemyError as e: handle(e, imageInfoDb)

        return imageInfoDb.Id

    # ----------------------------------------------------------------

    def process(self, metaData, scheme, thumbSize):
        '''
        @see: IMetaDataReferenceHandler.process
        '''
        assert isinstance(metaData, MetaDataMapped), 'Invalid meta data %s' % metaData
        try:
            metaData.Content = self.cdmImages.getURI(metaData.reference, scheme)
            metaData.IsAvailable = True
        except PathNotFound:
            metaData.IsAvailable = False
        return metaData

    # ----------------------------------------------------------------

    def _typeId(self):
        '''
        Provides the meta type image id. 
        '''
        if self._metaTypeId is None:
            try: metaType = self.session().query(MetaTypeMapped).filter(MetaTypeMapped.Key == self.imageTypeName).one()
            except NoResultFound:
                metaType = MetaTypeMapped()
                metaType.Key = self.imageTypeName
                self.session().add(metaType)
                self.session().flush((metaType,))
            self._metaTypeId = metaType.id
        return self._metaTypeId
