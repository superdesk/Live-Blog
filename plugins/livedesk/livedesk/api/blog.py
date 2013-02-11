'''
Created on May 4, 2012

@package: livedesk
@copyright: 2012 Sourcefabric o.p.s.
@license: http://www.gnu.org/licenses/gpl-3.0.txt
@author: Gabriel Nistor

API specifications for livedesk blog.
'''

from livedesk.api.domain_livedesk import modelLiveDesk
from ally.support.api.entity import Entity, IEntityCRUDService
from superdesk.language.api.language import LanguageEntity
from superdesk.user.api.user import User
from datetime import datetime
from ally.api.config import query, service, call, UPDATE
from ally.api.criteria import AsLikeOrdered, AsDateOrdered, AsBoolean
from ally.api.type import Iter
from livedesk.api.blog_type import BlogType

# --------------------------------------------------------------------

@modelLiveDesk
class Blog(Entity):
    '''
    Provides the blog model.
    '''
    Type = BlogType
    Language = LanguageEntity
    Creator = User
    Title = str
    Description = str
    OutputLink = str
    EmbedConfig = str
    CreatedOn = datetime
    IsLive = bool
    LiveOn = datetime
    LastUpdatedOn = datetime
    ClosedOn = datetime
    UpdatedOn = datetime

# --------------------------------------------------------------------

@query(Blog)
class QBlog(Entity):
    '''
    Provides the query for active blog model.
    '''
    title = AsLikeOrdered
    createdOn = AsDateOrdered
    liveOn = AsDateOrdered
    lastUpdatedOn = AsDateOrdered
    isLive = AsBoolean

# --------------------------------------------------------------------

@service((Entity, Blog))
class IBlogService(IEntityCRUDService):
    '''
    Provides the service methods for the blogs.
    '''

    @call
    def getBlog(self, blogId:Blog) -> Blog:
        '''
        Provides the blog based on the specified id
        '''

    @call
    def getAll(self, languageId:LanguageEntity=None, userId:User=None, offset:int=None, limit:int=None,
               detailed:bool=True, q:QBlog=None) -> Iter(Blog):
        '''
        Provides all the blogs.
        '''

    @call(webName='Live')
    def getLive(self, languageId:LanguageEntity=None, userId:User=None, q:QBlog=None) -> Iter(Blog):
        '''
        Provides all the blogs that are live at this moment.
        '''

    @call(webName='PutLive', method=UPDATE)
    def putLive(self, blogId:Blog.Id):
        '''
        Puts blog live
        @raise InputError: on invalid credentials or blog id 
        '''
