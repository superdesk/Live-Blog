'''
Created on May 3, 2012

@package: superdesk source
@copyright: 2012 Sourcefabric o.p.s.
@license: http://www.gnu.org/licenses/gpl-3.0.txt
@author: Gabriel Nistor

Contains the SQL alchemy implementation for source API.
'''

from ..api.source import ISourceService
from ..meta.source import SourceMapped
from ..meta.type import SourceTypeMapped
from ally.container.ioc import injected
from ally.exception import InputError, Ref
from ally.internationalization import _
from ally.support.api.util_service import copy
from ally.support.sqlalchemy.util_service import buildQuery, buildLimits, handle
from sql_alchemy.impl.entity import EntityGetCRUDServiceAlchemy
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm.exc import NoResultFound
from superdesk.source.api.source import Source

# --------------------------------------------------------------------

@injected
class SourceServiceAlchemy(EntityGetCRUDServiceAlchemy, ISourceService):
    '''
    Implementation for @see: ISourceService
    '''

    def __init__(self):
        '''
        Construct the source service.
        '''
        EntityGetCRUDServiceAlchemy.__init__(self, SourceMapped)

    def getAll(self, typeKey=None, offset=None, limit=None, q=None):
        '''
        @see: ISourceService.getAll
        '''
        sql = self.session().query(SourceMapped)
        if typeKey:
            sql = sql.join(SourceTypeMapped).filter(SourceTypeMapped.Key == typeKey)
        if q: sql = buildQuery(sql, q, SourceMapped)
        sql = buildLimits(sql, offset, limit)
        return sql.all()

    def insert(self, source):
        '''
        @see: ISourceService.insert
        '''
        assert isinstance(source, Source), 'Invalid source %s' % source
        sourceDb = SourceMapped()
        copy(source, sourceDb)
        sourceDb.typeId = self._typeId(source.Type)

        try:
            self.session().add(sourceDb)
            self.session().flush((sourceDb,))
        except SQLAlchemyError as e: handle(e, sourceDb)
        source.Id = sourceDb.Id
        return sourceDb.Id

    def update(self, source):
        '''
        @see: ISourceService.update
        '''
        assert isinstance(source, Source), 'Invalid source %s' % source
        sourceDb = self.session().query(SourceMapped).get(source.Id)
        if not sourceDb: raise InputError(Ref(_('Unknown source id'), ref=Source.Id))
        sourceDb.typeId = self._typeId(source.Type)

        try:
            self.session().flush((copy(source, sourceDb),))
        except SQLAlchemyError as e: handle(e, SourceMapped)

    # ----------------------------------------------------------------

    def _typeId(self, key):
        '''
        Provides the source type id that has the provided key.
        '''
        try:
            sql = self.session().query(SourceTypeMapped.id).filter(SourceTypeMapped.Key == key)
            return sql.one()[0]
        except NoResultFound:
            raise InputError(Ref(_('Invalid source type %(type)s') % dict(type=key), ref=Source.Type))
