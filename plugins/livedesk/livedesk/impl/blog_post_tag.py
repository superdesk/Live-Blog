'''
Created on August 26, 2013

@package: livedesk
@copyright: 2012 Sourcefabric o.p.s.
@license: http://www.gnu.org/licenses/gpl-3.0.txt
@author: Martin Saturka

Contains the SQL alchemy meta for livedesk blog post tags API.
'''

from livedesk.api.blog_post_tag import IBlogPostTagService
from livedesk.meta.blog_post_tag import BlogPostTagMapped
from livedesk.meta.blog import BlogMapped
from ally.container.ioc import injected
from ally.container.support import setup
from ally.support.sqlalchemy.util_service import buildLimits
from sql_alchemy.impl.entity import EntityServiceAlchemy
from superdesk.post.meta.post import PostMapped
from superdesk.tag.meta.tag import TagMapped
from superdesk.tag.meta.type import TagTypeMapped
from ally.api.extension import IterPart

# --------------------------------------------------------------------

@injected
@setup(IBlogPostTagService, name='blogPostTagService')
class BlogPostTagServiceAlchemy(EntityServiceAlchemy, IBlogPostTagService):
    '''
    Implementation for @see: IBlogPostTagService
    '''

    def __init__(self):
        '''
        Construct the blog post tag service.
        '''
        EntityServiceAlchemy.__init__(self, BlogPostTagMapped)

    def getAll(self, blogId=None, postId=None, tagTypeKey=None, offset=None, limit=None, detailed=False):
        '''
        @see: IBlogPostTagService.getAll
        '''
        sql = self.session().query(BlogPostTagMapped)
        if blogId:
            sql = sql.join(BlogMapped).filter(BlogMapped.Id == blogId)
        if postId:
            sql = sql.join(PostMapped).filter(PostMapped.Id == postId)
        if tagType:
            sql = sql.join(TagMapped, TagMapped.id == BlogPostTagMapped.typeId)
            sql = sql.join(TagTypeMapped, TagTypeMapped.id == TagMapped.typeId)
            sql = sql.filter(TagTypeMapped.Key == tagTypeKey)

        sqlLimit = buildLimits(sql, offset, limit)
        if detailed: return IterPart(sqlLimit.all(), sql.count(), offset, limit)
        return sqlLimit.all()
