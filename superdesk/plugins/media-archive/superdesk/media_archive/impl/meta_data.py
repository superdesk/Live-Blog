'''
Created on Apr 19, 2012

@package: superdesk media archive
@copyright: 2012 Sourcefabric o.p.s.
@license: http://www.gnu.org/licenses/gpl-3.0.txt
@author: Gabriel Nistor

SQL Alchemy based implementation for the meta data API. 
'''

from ..api.meta_data import IMetaDataService, QMetaData
from ..core.impl.meta_service_base import MetaDataServiceBaseAlchemy
from ..core.spec import IMetaDataHandler, IMetaDataReferencer, \
    IThumbnailReferencer
from ..meta.meta_data import MetaDataMapped
from ally.api.model import Content
from ally.container import wire
from ally.container.ioc import injected
from ally.exception import InputError
from ally.internationalization import _
from ally.support.sqlalchemy.util_service import handle
from ally.support.util_io import pipe, openURI, timestampURI
from ally.support.util_sys import pythonPath
from cdm.spec import ICDM
from datetime import datetime
from os import remove, makedirs, access, W_OK
from os.path import join, getsize, abspath, exists, isdir
from sqlalchemy.exc import SQLAlchemyError
from superdesk.media_archive.core.impl.meta_service_base import metaTypeFor, thumbnailFor
from superdesk.media_archive.meta.meta_data import META_TYPE_KEY

# --------------------------------------------------------------------

@injected
class MetaDataServiceAlchemy(MetaDataServiceBaseAlchemy, IMetaDataReferencer, IMetaDataService):
    '''
    Implementation for @see: IMetaDataService, and also provides services as the @see: IMetaDataReferencer
    '''

    processing_dir_path = join('workspace', 'media_archive', 'process_queue'); wire.config('processing_dir_path', doc='''
    The folder path where the content is queued for processing''')

    cdmArchive = ICDM
    # The archive CDM.
    thumbnailReferencer = IThumbnailReferencer; wire.entity('thumbnailReferencer')
    # Provides the thumbnail referencer
    metaDataHandlers = list
    # The handlers list used by the meta data in order to get the references.

    def __init__(self):
        '''
        Construct the meta data service.
        '''
        assert isinstance(self.processing_dir_path, str), 'Invalid processing directory %s' % self.processing_dir_path
        assert isinstance(self.cdmArchive, ICDM), 'Invalid archive CDM %s' % self.cdmArchive
        assert isinstance(self.thumbnailReferencer, IThumbnailReferencer), \
        'Invalid thumbnail referencer %s' % self.thumbnailReferencer
        assert isinstance(self.metaDataHandlers, list), 'Invalid reference handlers %s' % self.referenceHandlers
        MetaDataServiceBaseAlchemy.__init__(self, MetaDataMapped, QMetaData, self)

        if not exists(self.processing_dir_path): makedirs(self.processing_dir_path)
        if not isdir(self.processing_dir_path) or not access(self.processing_dir_path, W_OK):
            raise IOError('Unable to access the processing directory %s' % self.processing_dir_path)

    def deploy(self):
        '''
        Deploy the meta data and all handlers.
        '''
        self._metaType = metaTypeFor(self.session(), META_TYPE_KEY)
        self._thumbnail = thumbnailFor(self.session(), '%(size)s/other.jpg')
        referenceLast = self.thumbnailReferencer.timestampThumbnail(self._thumbnail.id)
        imagePath = join(pythonPath(), 'resources', 'other.jpg')
        if referenceLast is None or referenceLast < timestampURI(imagePath):
            self.thumbnailReferencer.processThumbnail(openURI(imagePath), self._thumbnail.id)

    # ----------------------------------------------------------------

    def populate(self, metaData, scheme, thumbSize=None):
        '''
        @see: IMetaDataReferencer.populate
        '''
        assert isinstance(metaData, MetaDataMapped), 'Invalid meta data %s' % metaData
        metaData.Content = self.cdmArchive.getURI(self._reference(metaData), scheme)
        return self.thumbnailReferencer.populate(metaData, scheme, thumbSize)

    # ----------------------------------------------------------------

    def insert(self, content):
        '''
        @see: IMetaDataService.insert
        '''
        assert isinstance(content, Content), 'Invalid content %s' % content
        if not content.getName(): raise InputError(_('No name specified for content'))

        metaData = MetaDataMapped()
        metaData.CreatedOn = datetime.now()
        metaData.Name = content.getName()
        metaData.Type = self._metaType.Key
        metaData.typeId = self._metaType.id
        metaData.thumbnailFormatId = self._thumbnail.id
        try:
            self.session().add(metaData)
            self.session().flush((metaData,))

            path = abspath(join(self.processing_dir_path, '.'.join((str(metaData.Id), metaData.Name))))
            with open(path, 'w+b') as fobj: pipe(content, fobj)
            metaData.SizeInBytes = getsize(path)

            self.session().flush((metaData,))

            #CDM not used
            #with open(path, 'rb') as fobj: self.cdmArchive.publishFromFile(self._reference(metaData), fobj)

            for handler in self.metaDataHandlers:
                assert isinstance(handler, IMetaDataHandler), 'Invalid handler %s' % handler
                if handler.process(metaData.Id, path): break
            else:
                remove(path)

        except SQLAlchemyError as e: handle(e, metaData)

        return metaData.Id

    # ----------------------------------------------------------------

    def _reference(self, metaData):
        '''
        Provides the refernce for the meta data.
        '''
        assert isinstance(metaData, MetaDataMapped), 'Invalid meta data %s' % metaData
        return ''.join((metaData.Type, '/', str(metaData.Id), '.', metaData.Name))
