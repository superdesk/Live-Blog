'''
Created on Apr 19, 2012

@package: superdesk media archive
@copyright: 2012 Sourcefabric o.p.s.
@license: http://www.gnu.org/licenses/gpl-3.0.txt
@author: Gabriel Nistor

SQL Alchemy based implementation for the meta data API.
'''

from ..api.meta_data import QMetaData
from ..core.impl.meta_service_base import MetaDataServiceBaseAlchemy
from ..core.spec import IMetaDataHandler, IMetaDataReferencer, IThumbnailManager
from ..meta.meta_data import MetaDataMapped
from ally.api.model import Content
from ally.cdm.spec import ICDM
from ally.container import wire, app
from ally.container.ioc import injected
from ally.container.support import setup
from ally.internationalization import _
from ally.support.util_sys import pythonPath
from os.path import join, getsize, abspath
from superdesk.media_archive.api.meta_data import IMetaDataUploadService
from superdesk.media_archive.core.impl.meta_service_base import metaTypeFor, \
    thumbnailFormatFor
from superdesk.media_archive.core.impl.query_service_creator import \
    ISearchProvider
from superdesk.media_archive.meta.meta_data import META_TYPE_KEY
from superdesk.media_archive.meta.meta_info import MetaInfoMapped
from ally.api.error import InputError
from superdesk.language.meta.language import LanguageAvailable
from ally.api.validate import validate

# --------------------------------------------------------------------

@injected
@setup(IMetaDataUploadService, name='metaDataService')
@validate(MetaDataMapped)
class MetaDataServiceAlchemy(MetaDataServiceBaseAlchemy, IMetaDataReferencer, IMetaDataUploadService):
    '''Implementation for @see: IMetaDataService, @see: IMetaDataUploadService , and also provides services
    as the @see: IMetaDataReferencer
    '''

    format_file_name = '%(id)s.%(name)s'; wire.config('format_file_name', doc='''
    The format for the files names in the media archive''')
    format_thumbnail = '%(size)s/other.jpg'; wire.config('format_thumbnail', doc='''
    The format for the unknown thumbnails in the media archive''')

    cdmArchive = ICDM; wire.entity('cdmArchive')
    thumbnailManager = IThumbnailManager; wire.entity('thumbnailManager')
    metaDataHandlers = list; wire.entity('metaDataHandlers')
    # The handlers list used by the meta data in order to get the references.

    searchProvider = ISearchProvider; wire.entity('searchProvider')
    # The search provider that will be used to manage all search related activities
    default_media_language = 'en'; wire.config('default_media_language')

    languageId = None


    def __init__(self):
        '''Construct the meta data service.'''
        assert isinstance(self.format_file_name, str), 'Invalid format file name %s' % self.format_file_name
        assert isinstance(self.format_thumbnail, str), 'Invalid format thumbnail %s' % self.format_thumbnail
        assert isinstance(self.cdmArchive, ICDM), 'Invalid archive CDM %s' % self.cdmArchive
        assert isinstance(self.thumbnailManager, IThumbnailManager), 'Invalid thumbnail manager %s' % self.thumbnailManager
        assert isinstance(self.metaDataHandlers, list), 'Invalid reference handlers %s' % self.referenceHandlers
        assert isinstance(self.searchProvider, ISearchProvider), 'Invalid search provider %s' % self.searchProvider

        MetaDataServiceBaseAlchemy.__init__(self, MetaDataMapped, QMetaData, self, self.cdmArchive, self.thumbnailManager)

        self._thumbnailFormatId = self._metaTypeId = None

    # ----------------------------------------------------------------

    def insert(self, userId, content, scheme, thumbSize=None):
        '''
        @see: IMetaDataService.insert
        '''
        assert isinstance(content, Content), 'Invalid content %s' % content
        if not content.name: raise InputError(_('No name specified for content'))

        if self.languageId is None:
            self.languageId = self.session().query(LanguageAvailable).filter(LanguageAvailable.Code == self.default_media_language).one().id

        metaData = MetaDataMapped()
        metaData.Creator = userId
        metaData.Name = content.name

        metaData.typeId = self.metaTypeId()
        metaData.Type = META_TYPE_KEY
        metaData.thumbnailFormatId = self.thumbnailFormatId()

        self.session().add(metaData)
        self.session().flush((metaData,))

        path = self.format_file_name % {'id': metaData.Id, 'name': metaData.Name}
        path = ''.join((META_TYPE_KEY, '/', self.generateIdPath(metaData.Id), '/', path))
        contentPath = self.cdmArchive.getURI(path, 'file')

        self.cdmArchive.publishContent(path, content)
        metaData.content = path
        metaData.SizeInBytes = getsize(contentPath)

        found = False
        for handler in self.metaDataHandlers:
            assert isinstance(handler, IMetaDataHandler), 'Invalid handler %s' % handler
            if handler.processByInfo(metaData, contentPath, content.type):
                metaInfo = handler.addMetaInfo(metaData, self.languageId)
                found = True
                break
        else:
            for handler in self.metaDataHandlers:
                if handler.process(metaData, contentPath):
                    metaInfo = handler.addMetaInfo(metaData, self.languageId)
                    found = True
                    break

        if found:
            self.session().merge(metaData)
            self.session().flush((metaData,))
        else:
            metaInfo = MetaInfoMapped()
            metaInfo.MetaData = metaData.Id
            metaInfo.Language = self.languageId

            self.session().add(metaInfo)
            self.session().flush((metaData, metaInfo,))

        self.searchProvider.update(metaInfo, metaData)

        if metaData.content != path:
            self.cdmArchive.republish(path, metaData.content)

        return self.getById(metaData.Id, scheme, thumbSize)

    # ----------------------------------------------------------------

    @app.populate
    def populateThumbnail(self):
        '''Populates the thumbnail for other resources.'''
        self.thumbnailManager.putThumbnail(self.thumbnailFormatId(),
                                           abspath(join(pythonPath(), 'resources', 'other.jpg')))

    # ----------------------------------------------------------------

    def metaTypeId(self):
        '''Provides the meta type id.'''
        if self._metaTypeId is None: self._metaTypeId = metaTypeFor(self.session(), META_TYPE_KEY).id
        return self._metaTypeId

    def thumbnailFormatId(self):
        '''Provides the thumbnail format id.'''
        if not self._thumbnailFormatId: self._thumbnailFormatId = thumbnailFormatFor(self.session(), self.format_thumbnail).id
        return self._thumbnailFormatId

    def generateIdPath (self, id):
        # TOTO: add comment
        return '{0:03d}'.format((id // 1000) % 1000)
