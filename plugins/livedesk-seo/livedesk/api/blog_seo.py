'''
Created on Feb 5, 2014

@package: livedesk
@copyright: 2014 Sourcefabric o.p.s.
@license: http://www.gnu.org/licenses/gpl-3.0.txt
@author: Ioan v. Pocol

API specifications for liveblog seo.
'''

from ally.support.api.entity import Entity, IEntityService, QEntity
from livedesk.api.blog import Blog
from datetime import datetime
from livedesk.api.domain_livedesk import modelLiveDesk
from ally.api.config import query, service, call, UPDATE
from ally.api.criteria import AsRangeOrdered, AsDateTimeOrdered, AsBoolean,\
    AsLikeOrdered
from livedesk.api.blog_theme import BlogTheme
from ally.api.type import Iter

# --------------------------------------------------------------------

@modelLiveDesk(name='Seo')
class BlogSeo(Entity):
    '''
    Provides the blog seo model. 
    '''
    Blog = Blog
    BlogTheme = BlogTheme
    RefreshActive = bool
    RefreshInterval = int
    MaxPosts = int
    CallbackActive = bool
    CallbackURL = str
    NextSync = datetime
    LastCId = int
    LastSync = datetime
    LastBlocked = datetime

# --------------------------------------------------------------------

@query(BlogSeo)
class QBlogSeo(QEntity):
    '''
    Provides the query for BlogSeo.
    '''
    refreshActive = AsBoolean
    refreshInterval = AsRangeOrdered
    maxPosts = AsRangeOrdered
    callbackActive = AsBoolean
    callbackURL = AsLikeOrdered
    nextSync = AsDateTimeOrdered
    lastCId = AsRangeOrdered
    lastSync = AsDateTimeOrdered
    lastBlocked = AsDateTimeOrdered
    
# --------------------------------------------------------------------

@service((Entity, BlogSeo), (QEntity, QBlogSeo))
class IBlogSeoService(IEntityService):
    '''
    Provides the service methods for the blog seo.
    '''  
    
    @call
    def getAll(self, blogId:Blog.Id=None, themeId:BlogTheme.Id=None, offset:int=None, limit:int=None,
               detailed:bool=True, q:QBlogSeo=None) -> Iter(BlogSeo):
        '''
        Provides the list of all blog seo.
        '''
            
    @call(webName="existsChanges", method=UPDATE)
    def existsChanges(self, blogSeoId:BlogSeo.Id, lastCid:BlogSeo.LastCId) -> bool:
        '''
        Returns true if the blog has been updated since last sync
        '''   
    @call(webName="checkTimeout", method=UPDATE)
    def checkTimeout(self, blogSeoId:BlogSeo.Id, timeout:int) -> bool:
        '''
        Returns true if the last activity is older than timeout and if it is older update the last activity value
        '''       
    @call(webName="nextSync", method=UPDATE)
    def updateNextSync(self, blogSeoId:BlogSeo.Id, crtTime:datetime):
        '''
        Calculate the next sync datetime for already expired sync 
        '''                       