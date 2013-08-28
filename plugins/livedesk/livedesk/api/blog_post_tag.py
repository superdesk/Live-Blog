'''
Created on August 26, 2013

@package: livedesk
@copyright: 2012 Sourcefabric o.p.s.
@license: http://www.gnu.org/licenses/gpl-3.0.txt
@author: Martin Saturka

API specifications for livedesk blog post tags.
'''

from ally.api.config import service, call
from ally.support.api.entity import Entity, IEntityService
from livedesk.api.blog import Blog
from livedesk.api.domain_livedesk import modelLiveDesk
from superdesk.tag.api.tag import Tag
from superdesk.post.api.post import Post

# --------------------------------------------------------------------

@modelLiveDesk
class BlogPostTag(Entity):
    '''
    Provides the blog post tag model.
    '''
    Blog = Blog
    Post = Post
    Tag = Tag

# --------------------------------------------------------------------

# No query

# --------------------------------------------------------------------

@service((Entity, BlogPostTag))
class IBlogPostTagService(IEntityService):
    '''
    BlogPostTag model service interface
    '''

    @call
    def getAll(self, blogId:Blog.Id=None, postId:Post.Id=None, tagType:TagTypeKey.Key=None, offset:int=None,
               limit:int=LIMIT_DEFAULT, detailed:bool=True) -> Iter(BlogPostTag):
        '''
        Provides all the available blog post tags.
        '''

    # TODO: basic crud operations with the type key use
