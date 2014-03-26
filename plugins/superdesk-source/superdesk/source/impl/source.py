'''
Created on May 3, 2012

@package: superdesk source
@copyright: 2012 Sourcefabric o.p.s.
@license: http://www.gnu.org/licenses/gpl-3.0.txt
@author: Gabriel Nistor

Contains the SQL alchemy implementation for source API.
'''

from ..api.source import ISourceService, QSource
from ..meta.source import SourceMapped
from ..meta.type import SourceTypeMapped
from ally.container.ioc import injected
from ally.container.support import setup
from ally.exception import InputError, Ref
from ally.internationalization import _
from ally.support.api.util_service import copy
from ally.support.sqlalchemy.util_service import buildQuery, buildLimits, handle
from sql_alchemy.impl.entity import EntityGetCRUDServiceAlchemy
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm.exc import NoResultFound
from superdesk.source.api.source import Source
from ally.api.extension import IterPart
from ally.api.criteria import AsLike

#TODO: Hack to be able to get the list of the chained blog sources for a blog;
#It should be removed when the new version of ally-py is used 
from livedesk.meta.blog import BlogSourceDB
from sqlalchemy.orm.util import aliased

# --------------------------------------------------------------------

ALL_NAMES = (SourceMapped.Name, SourceMapped.URI)

@injected
@setup(ISourceService, name='sourceService')
class SourceServiceAlchemy(EntityGetCRUDServiceAlchemy, ISourceService):
    '''
    Implementation for @see: ISourceService
    '''

    def __init__(self):
        '''
        Construct the source service.
        '''
        EntityGetCRUDServiceAlchemy.__init__(self, SourceMapped, QSource)

    def getAll(self, typeKey=None, offset=None, limit=None, detailed=False, q=None):
        '''
        @see: ISourceService.getAll
        '''
        sql = self.session().query(SourceMapped)
        if typeKey:
            sql = sql.join(SourceTypeMapped).filter(SourceTypeMapped.Key == typeKey)
        if q:
            assert isinstance(q, QSource), 'Invalid source query %s' % q
            sql = buildQuery(sql, q, SourceMapped)
            if QSource.all in q:
                filter = None
                if AsLike.like in q.all:
                    for col in ALL_NAMES:
                        filter = col.like(q.all.like) if filter is None else filter | col.like(q.all.like)
                elif AsLike.ilike in q.all:
                    for col in ALL_NAMES:
                        filter = col.ilike(q.all.ilike) if filter is None else filter | col.ilike(q.all.ilike)
                sql = sql.filter(filter)
            
            #TODO: Hack to be able to get the list of the chained blog sources for a blog;
            #It should be removed when the new version of ally-py is used    
            if QSource.blogId in q:
                sqlIn = self.session().query(BlogSourceDB.source).filter(BlogSourceDB.blog == q.blogId.equal)
                sql = sql.filter(SourceMapped.Id.in_(sqlIn))    

        sqlLimit = buildLimits(sql, offset, limit)
        if detailed: return IterPart(sqlLimit.all(), sql.count(), offset, limit)
        return sqlLimit.all()

    def getOriginalSource(self, source):
        originalSource = aliased(SourceMapped, name='original_source')
        
        sql = self.session().query(originalSource)
        sql = sql.join(SourceMapped, originalSource.URI == SourceMapped.OriginURI)
        sql = sql.filter(SourceMapped.Id == source)
        
        return sql.one().Id  

    def insert(self, source):
        '''
        @see: ISourceService.insert
        '''
        assert isinstance(source, Source), 'Invalid source %s' % source
        
        if source.URI:
            list = source.URI.split('//')
            source.URI = '//' + list[-1]
            
        if source.OriginURI:
            list = source.OriginURI.split('//')
            source.OriginURI = '//' + list[-1]    
        
        sourceDb = SourceMapped()
        sourceDb.typeId = self._typeId(source.Type)
        copy(source, sourceDb, exclude=('Type',))

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
        
        if source.URI:
            list = source.URI.split('//')
            source.URI = '//' + list[-1]
            
        if source.OriginURI:
            list = source.OriginURI.split('//')
            source.OriginURI = '//' + list[-1]    
        
        sourceDb = self.session().query(SourceMapped).get(source.Id)
        if not sourceDb: raise InputError(Ref(_('Unknown source id'), ref=Source.Id))
        if Source.Type in source: sourceDb.typeId = self._typeId(source.Type)

        try:
            self.session().flush((copy(source, sourceDb, exclude=('Type',)),))
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
