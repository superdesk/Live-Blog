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
from ally.api.config import query, service, call, UPDATE, DELETE, INSERT
from ally.api.criteria import AsLikeOrdered, AsDateOrdered, AsBoolean
from ally.api.type import Iter
from livedesk.api.blog_type import BlogType
from superdesk.source.api.source import Source
from support.api.configuration import IConfigurationService

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
    DeletedOn = datetime

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
    isOpen = AsBoolean

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
    
    @call(webName='Hide', method=UPDATE)
    def hide(self, blogId:Blog.Id):
        '''
        Hide the blog
        @raise InputError: on invalid credentials or blog id 
        '''    
        
    @call(webName='Unhide', method=UPDATE)
    def unhide(self, blogId:Blog.Id):
        '''
        Unhide the blog
        @raise InputError: on invalid credentials or blog id 
        '''    
        

# --------------------------------------------------------------------

@service
class IBlogSourceService:
    @call
    def getSource(self, blogId:Blog.Id, sourceId:Source.Id) -> Source:
        '''
        Gets source for source chained.
        This methods is necessary for getting the right URLs on chained-blog sources.

        @param blogId: Blog.Id
            The blog identifier
        @param source: Source
            The source model
        '''

    @call
    def getSources(self, blogId:Blog.Id) -> Iter(Source):
        '''
        Returns a list of blog sources

        @param blogId: Blog.Id
            The blog identifier
        '''

    @call(method=INSERT)
    def addSource(self, blogId:Blog.Id, source:Source) -> Source.Id:
        '''
        Adds a source to a blog.

        @param blogId: Blog.Id
            The blog identifier
        @param source: Source
            The source model
        @raise InputError: on invalid source id
        '''

    @call(method=DELETE)
    def deleteSource(self, blogId:Blog.Id, sourceId:Source.Id) -> bool:
        '''
        Removes a source from the blog.

        @param blogId: Blog.Id
            The blog identifier
        @param sourceId: Source.Id
            The source identifier
        @raise InputError: on invalid source id
        '''

# --------------------------------------------------------------------

@service((Entity, Blog))
class IBlogConfigurationService(IConfigurationService):
    '''
    Provides the blog configuration service.
    '''
