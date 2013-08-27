'''
Created on August 27, 2013

@package: livedesk
@copyright: 2013 Sourcefabric o.p.s.
@license: http://www.gnu.org/licenses/gpl-3.0.txt
@author: Martin Saturka

API specifications for blog sms.
'''

from ..api.blog_post import BlogPost, QBlogPost
from ally.api.config import service, call, INSERT
from ally.api.type import Iter
from ally.support.api.keyed import Entity
from livedesk.api.domain_livedesk import modelLiveDesk
from livedesk.api.blog import Blog
from superdesk.post.api.post import Post

from ally.api.criteria import AsRangeOrdered, AsBoolean, AsLike

# --------------------------------------------------------------------

@modelLiveDesk(name='SMS')
class BlogSMS:
    '''
    Separate model for the SMS itself.
    '''
    Post = Post
    Feed = str

    #UserName = str
    #CommentText = str
    #CommentSource = str

# --------------------------------------------------------------------

@query(BlogSMS)
class QBlogSMS:
    '''
    Provides the query for SMS specifying.
    '''
    hidden = AsBoolean

# --------------------------------------------------------------------

@service
class IBlogSMSService:
    '''
    Provides the service methods for the blog sms.
    '''

    #@call(webName='SMS')
    @call
    def getMessages(self, blogId:Blog.Id, sourceId:Source.Id=None, offset:int=None, limit:int=None, detailed:bool=True,
                    q:QBlogSMS=None) -> Iter(BlogSMS):
        '''
        Lists SMS posts relevant to the specified blog.
        '''
