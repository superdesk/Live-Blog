'''
Created on May 29, 2013

@package: support
@copyright: 2013 Sourcefabric o.p.s.
@license: http://www.gnu.org/licenses/gpl-3.0.txt
@author: Martin Saturka

Contains the SQL alchemy meta for the file-info links API.
'''

from ..api.file_link import IFileLinkService
from ..meta.file_link import FileLinkDescription
from superdesk.media_archive.api.meta_info import MetaInfo, QMetaInfo
from superdesk.media_archive.meta.meta_info import MetaInfoMapped
from ally.container.ioc import injected
from ally.container.support import setup
from ally.support.sqlalchemy.session import SessionSupport
from ally.exception import InputError, Ref
from ally.internationalization import _
from ally.api.extension import IterPart
from ally.support.sqlalchemy.util_service import buildQuery, buildLimits
from ally.support.util_sys import callerGlobals
from sqlalchemy.orm.exc import NoResultFound
from sqlalchemy.sql.expression import exists, and_

# --------------------------------------------------------------------

def createFileLinkImpl(service, mapped):
    '''
    Generator of particular file-link implementations
    '''
    assert issubclass(service, IFileLinkService), 'Invalid service. It should extend the IFileLinkService'
    assert issubclass(mapped, FileLinkDescription), 'Invalid DB mapping. It should extend the FileLinkDescription mapping'

    namespace = {'FileLinkDB': mapped, '__module__': callerGlobals()['__name__']}
    return type('%sAlchemy' % service.__name__[1:], (FileLinkServiceAlchemy, service), namespace)

# --------------------------------------------------------------------

@injected
@setup(IFileLinkService, name='fileLinkService')
class FileLinkServiceAlchemy(SessionSupport, IFileLinkService):
    '''
    Implementation for @see: IFileLinkService
    '''
    
    FileLinkDB = FileLinkDescription
    # variable for the DB linking class to be used

    metaDataUploadService = IMetaDataUploadService; wire.entity('metaDataUploadService')

    def getById(self, parentId, fileInfoId):
        '''
        @see: IFileLinkService.getById
        '''
        sql = self.session().query(MetaInfoMapped)
        sql = sql.join(self.FileLinkDB, self.FileLinkDB.file == MetaInfoMapped.Id)
        sql = sql.filter(self.FileLinkDB.parent == parentId)
        sql = sql.filter(self.FileLinkDB.file == fileInfoId)
        try:
            return sql.one()
        except NoResultFound: raise InputError(Ref(_('The file info is not linked'),))

    def getAll(self, parentId, offset=None, limit=None, detailed=False, q=None):
        '''
        @see: IFileLinkService.getAll
        '''
        sql = self.session().query(MetaInfoMapped)
        sql = sql.join(self.FileLinkDB, self.FileLinkDB.file == MetaInfoMapped.Id)
        sql = sql.filter(self.FileLinkDB.parent == parentId)

        if q:
            assert isinstance(q, QMetaInfo), 'Invalid query'
            sql = buildQuery(sql, q, self.MetaInfoMapped)

        sqlLimit = buildLimits(sql, offset, limit)
        if detailed: return IterPart(sqlLimit.all(), sql.count(), offset, limit)
        return sqlLimit.all()

    def attachFile(self, parentId, fileInfoId):
        '''
        @see: IFileLinkService.attachFile
        '''
        if self.session().query(exists().where(and_(self.FileLinkDB.file == fileInfoId, self.FileLinkDB.parent == parentId))).scalar():
            raise InputError(Ref(_('File already attached'),))

        fileLink = self.FileLinkDB()
        fileLink.parent = parentId
        fileLink.file = fileId

        self.session().add(fileLink)
        self.session().flush((fileLink,))

        return

    def detachFile(self, parentId:Entity.Id, fileInfoId:MetaData.Id):
        '''
        @see: IFileLinkService.detachFile
        '''
        sql = self.session().query(self.FileLinkDB)
        sql = sql.filter(self.FileLinkDB.file == fileInfoId)
        sql = sql.filter(self.FileLinkDB.parent == parentId)

        return sql.delete() > 0

