'''
Created on April 26, 2013

@package: livedesk
@copyright: 2013 Sourcefabric o.p.s.
@license: http://www.gnu.org/licenses/gpl-3.0.txt
@author: Mugur Rus

API implementation for liveblog sync.
'''

from livedesk.api.blog_sync import IBlogSyncService, QBlogSync
from sql_alchemy.impl.entity import EntityServiceAlchemy
from ally.container.support import setup
from ally.support.sqlalchemy.util_service import buildQuery, buildLimits
from superdesk.source.meta.source import SourceMapped
from superdesk.source.meta.type import SourceTypeMapped
from ally.api.extension import IterPart
import datetime
from sqlalchemy.sql.expression import or_
from livedesk.meta.blog import BlogSourceDB
from livedesk.meta.blog_sync import BlogSyncMapped
from ally.container import wire

# --------------------------------------------------------------------

@setup(IBlogSyncService, name='blogSyncService')
class BlogSyncServiceAlchemy(EntityServiceAlchemy, IBlogSyncService):
    '''
    Implementation for @see IBlogSyncService
    '''
    
    blog_provider_type = 'blog provider'; wire.config('blog_provider_type', doc='''
    Key of the source type for blog providers''')
    sms_provider_type = 'sms provider'; wire.config('sms_provider_type', doc='''
    Key of the source type for sms providers''')

    def __init__(self):
        '''
        Construct the blog sync service.
        '''
        EntityServiceAlchemy.__init__(self, BlogSyncMapped, QBlogSync)
        
    def checkTimeout(self, blogSyncId, timeout):
        '''
        @see IBlogSyncService.checkTimeout
        '''  
        crtTime = datetime.datetime.now().replace(microsecond=0)  
        referenceTime = crtTime - datetime.timedelta(seconds=timeout)
        
        sql = self.session().query(BlogSyncMapped)
        sql = sql.filter(BlogSyncMapped.Id == blogSyncId)
        sql = sql.filter(or_(BlogSyncMapped.LastActivity == None, BlogSyncMapped.LastActivity < referenceTime))
        result = sql.update({BlogSyncMapped.LastActivity : crtTime}) 
        self.session().commit()       

        return result

    def getBySourceType(self, sourceType, offset=None, limit=None, detailed=False, q=None):
        '''
        @see IBlogSyncService.getBySourceType
        '''
        sql = self.session().query(BlogSyncMapped)
        if q:
            assert isinstance(q, QBlogSync), 'Invalid blog sync query %s' % q
            sql = buildQuery(sql, q, BlogSyncMapped)

        sql = sql.join(SourceMapped, SourceMapped.Id == BlogSyncMapped.Source)
        sql = sql.join(BlogSourceDB, SourceMapped.Id == BlogSourceDB.source)

        sql_prov = self.session().query(SourceMapped.URI)
        sql_prov = sql_prov.join(SourceTypeMapped, SourceTypeMapped.id == SourceMapped.typeId)
        sql_prov = sql_prov.filter(SourceTypeMapped.Key == sourceType)

        sql = sql.filter(SourceMapped.OriginURI.in_(sql_prov))

        sqlLimit = buildLimits(sql, offset, limit)
        if detailed: return IterPart(sqlLimit.all(), sql.count(), offset, limit)
        return sqlLimit.all()
        

    def getByBlog(self, blogId, offset=None, limit=None, detailed=False, q=None):        
        '''
        @see IBlogSyncService.getByBlog
        '''
        sql = self.session().query(BlogSyncMapped)
        if q:
            assert isinstance(q, QBlogSync), 'Invalid blog sync query %s' % q
            sql = buildQuery(sql, q, BlogSyncMapped)

        sql = sql.join(SourceMapped, SourceMapped.Id == BlogSyncMapped.Source)
        sql = sql.join(BlogSourceDB, SourceMapped.Id == BlogSourceDB.source)
        sql = sql.filter(BlogSourceDB.blog == blogId)

        sql_prov = self.session().query(SourceMapped.URI)
        sql_prov = sql_prov.join(SourceTypeMapped, SourceTypeMapped.id == SourceMapped.typeId)
        sql_prov = sql_prov.filter(SourceTypeMapped.Key == self.blog_provider_type)

        sql = sql.filter(SourceMapped.OriginURI.in_(sql_prov))

        sqlLimit = buildLimits(sql, offset, limit)
        if detailed: return IterPart(sqlLimit.all(), sql.count(), offset, limit)
        return sqlLimit.all()
    
    def update(self, entity):
        '''
        @see: IBlogSyncService.update
        '''
        EntityServiceAlchemy.update(self, entity)
        self.session().commit()
