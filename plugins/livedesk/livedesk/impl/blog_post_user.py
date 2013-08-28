'''
Created on August 28, 2013

@package: livedesk
@copyright: 2012 Sourcefabric o.p.s.
@license: http://www.gnu.org/licenses/gpl-3.0.txt
@author: Martin Saturka

Contains the SQL alchemy meta for livedesk blog post users API.
'''

from livedesk.api.source import IBlogPostUserService
from livedesk.meta.source import BlogPostUserMapped
from livedesk.meta.blog import BlogMapped
from ally.container.ioc import injected
from ally.container.support import setup
from ally.support.sqlalchemy.util_service import buildLimits
from sql_alchemy.impl.entity import EntityServiceAlchemy
from superdesk.post.meta.post import PostMapped
from superdesk.tag.meta.tag import UserMapped
from ally.api.extension import IterPart

# --------------------------------------------------------------------

@injected
@setup(IBlogPostUserService, name='blogPostUserService')
class BlogPostUserServiceAlchemy(EntityServiceAlchemy, IBlogPostUserService):
    '''
    Implementation for @see: IBlogPostUserService
    '''

    def __init__(self):
        '''
        Construct the blog post user service.
        '''
        EntityServiceAlchemy.__init__(self, BlogPostUserMapped)

    def getAll(self, blogId=None, postId=None, offset=None, limit=None, detailed=False):
        '''
        @see: IBlogPostTagService.getAll
        '''
        return ()
