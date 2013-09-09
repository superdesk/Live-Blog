'''
Created on August 26, 2013

@package: livedesk
@copyright: 2012 Sourcefabric o.p.s.
@license: http://www.gnu.org/licenses/gpl-3.0.txt
@author: Martin Saturka

API specifications for livedesk blog post tags.
'''

from ally.api.config import service, call, LIMIT_DEFAULT, UPDATE, DELETE
from livedesk.api.blog import Blog
from livedesk.api.domain_livedesk import modelLiveDesk
from superdesk.tag.api.tag import Tag
from superdesk.tag.api.type import TagType
from superdesk.post.api.post import Post
from ally.api.type import Iter

# --------------------------------------------------------------------

# No model

# --------------------------------------------------------------------

# No query

# --------------------------------------------------------------------

@service
class IBlogPostTagService:
    '''
    BlogPostTag service interface
    '''

    @call
    def getTagType(self, blogId:Blog.Id, postId:Post.Id, tagTypeKey:TagType.Key) -> TagType:
        '''
        Gets tag type.
        This methods is necessary for getting the right URLs on blog-post tag types.

        @param blogId: Blog.Id
            The blog identifier
        @param postId: Post.Id
            The post identifier
        @param tagTypeKey: TagType.Key
            The tag type identifier
        '''

    @call
    def getAllTagTypes(self, blogId:Blog.Id, postId:Post.Id, offset:int=None,
               limit:int=LIMIT_DEFAULT, detailed:bool=True) -> Iter(TagType):
        '''
        Provides all tag types.
        This methods is necessary for getting URLs for tag listing by blog-post tag types.
        '''

    @call
    def getAll(self, blogId:Blog.Id, postId:Post.Id, tagTypeKey:TagType.Key, offset:int=None,
               limit:int=LIMIT_DEFAULT, detailed:bool=True) -> Iter(Tag):
        '''
        Provides all the available blog post tags of a tag type.
        '''

    @call(method=UPDATE, webName='Attach')
    def attach(self, blogId:Blog.Id, postId:Post.Id, tagTypeKey:TagType.Key, tagKey:Tag.Key):
        '''
        Attaches the tag to the blog post.
        '''

    @call(method=DELETE, webName='Detach')
    def detach(self, blogId:Blog.Id, postId:Post.Id, tagTypeKey:TagType.Key, tagKey:Tag.Key) -> bool:
        '''
        Detaches the tag from the blog post.
        '''
