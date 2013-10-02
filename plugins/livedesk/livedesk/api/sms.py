'''
Created on August 27, 2013

@package: livedesk
@copyright: 2013 Sourcefabric o.p.s.
@license: http://www.gnu.org/licenses/gpl-3.0.txt
@author: Martin Saturka

API specifications for blog sms.
'''

from ally.api.config import service, call, LIMIT_DEFAULT
from ally.api.type import Iter
from livedesk.api.blog import Blog
from superdesk.post.api.post import Post
from superdesk.source.api.source import Source
from livedesk.api.blog_post import QBlogPost

# --------------------------------------------------------------------

# no model

# --------------------------------------------------------------------

# no query

# --------------------------------------------------------------------

@service
class IBlogSMSService:
    '''
    Provides the service methods for the blog sms.
    '''

    @call(webName='SMS')
    def getSources(self, blogId:Blog.Id, offset:int=None, limit:int=LIMIT_DEFAULT, detailed:bool=True) -> Iter(Source):
        '''
        Lists SMS sources relevant to the specified blog.
        '''

    @call(webName='SMS')
    def getMessages(self, blogId:Blog.Id, sourceId:Source.Id=None, offset:int=None, limit:int=LIMIT_DEFAULT, detailed:bool=True,
                    q:QBlogPost=None) -> Iter(Post):
        '''
        Lists SMS posts relevant to the specified blog.
        '''

    @call(webName='PublishedSMS')
    def getPublishedMessages(self, blogId:Blog.Id, sourceId:Source.Id=None, offset:int=None, limit:int=LIMIT_DEFAULT, detailed:bool=True,
                    q:QBlogPost=None) -> Iter(Post):
        '''
        Lists published SMS posts relevant to the specified blog.
        '''

    @call(webName='UnpublishedSMS')
    def getUnpublishedMessages(self, blogId:Blog.Id, sourceId:Source.Id=None, offset:int=None, limit:int=LIMIT_DEFAULT, detailed:bool=True,
                    q:QBlogPost=None) -> Iter(Post):
        '''
        Lists unpublished SMS posts relevant to the specified blog.
        '''
