'''
Created on April 26, 2013

@package: livedesk
@copyright: 2013 Sourcefabric o.p.s.
@license: http://www.gnu.org/licenses/gpl-3.0.txt
@author: Mugur Rus

API implementation for liveblog sync.
'''

from livedesk.api.blog_sync import IBlogSyncService, QBlogSync, BlogSync
from sql_alchemy.impl.entity import EntityServiceAlchemy
from ally.container.support import setup
from livedesk.meta.blog_sync import BlogSyncMapped
from sqlalchemy.sql.functions import current_timestamp
from superdesk.source.meta.source import SourceMapped
from superdesk.source.meta.type import SourceTypeMapped
from ally.container import wire
from sqlalchemy.sql.expression import or_
from sql_alchemy.support.util_service import buildQuery, iterateCollection
from ally.api.validate import validate

# --------------------------------------------------------------------

@setup(IBlogSyncService, name='blogSyncService')
@validate(BlogSyncMapped)
class BlogSyncServiceAlchemy(EntityServiceAlchemy, IBlogSyncService):
    '''
    Implementation for @see IBlogSyncService
    '''
    blog_provider_type = 'blog provider'; wire.config('blog_provider_type', doc='''
    Key of the source type for blog providers''')

    def __init__(self):
        '''
        Construct the blog sync service.
        '''
        EntityServiceAlchemy.__init__(self, BlogSyncMapped, QBlogSync)

    def getAll(self, q=None, **options):
        '''
        @see IBlogSyncService.getAll
        '''
        sql = self.session().query(BlogSyncMapped)
        if q:
            assert isinstance(q, QBlogSync), 'Invalid blog sync query %s' % q
            sql = buildQuery(sql, q, BlogSyncMapped)

        sql = sql.join(SourceMapped, SourceMapped.Id == BlogSyncMapped.Source)

        sql_prov = self.session().query(SourceMapped.URI)
        sql_prov = sql_prov.join(SourceTypeMapped)
        sql_prov = sql_prov.filter(SourceTypeMapped.Key == self.blog_provider_type)

        sql = sql.filter(or_(SourceMapped.OriginURI == None, SourceMapped.OriginURI.in_(sql_prov)))
        return iterateCollection(sql, **options)

    def getBlogSync(self, blog, q, **options):
        '''
        @see IBlogSyncService.getBlogSync
        '''
        sql = self.session().query(BlogSyncMapped).filter(BlogSyncMapped.Blog == blog)
        if q: sql = buildQuery(sql, q, BlogSyncMapped)

        sql = sql.join(SourceMapped, SourceMapped.Id == BlogSyncMapped.Source)

        sql_prov = self.session().query(SourceMapped.URI)
        sql_prov = sql_prov.join(SourceTypeMapped)
        sql_prov = sql_prov.filter(SourceTypeMapped.Key == self.blog_provider_type)

        sql = sql.filter(or_(SourceMapped.OriginURI == None, SourceMapped.OriginURI.in_(sql_prov)))
        return iterateCollection(sql, options)

    def insert(self, blogSync):
        '''
        @see IBlogSyncService.insert
        '''
        assert isinstance(blogSync, BlogSync), 'Invalid blog sync %s' % blogSync

#        if blogSync.Auto and blogSync.Start is None:
#            blogSync.Start = current_timestamp()
        return super().insert(blogSync)

    def update(self, blogSync):
        '''
        @see IBlogSyncService.update
        '''
        assert isinstance(blogSync, BlogSync), 'Invalid blog sync %s' % blogSync

        blogSyncDb = self.getById(blogSync.Id)

        if blogSync.Auto and not blogSyncDb.Auto and blogSync.Start is None:
            blogSync.Start = current_timestamp()
        return super().update(blogSync)
