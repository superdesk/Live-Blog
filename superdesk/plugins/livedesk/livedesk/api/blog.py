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
from ally.api.config import query, service, call
from ally.api.criteria import AsLikeOrdered, AsDateOrdered
from ally.api.type import Iter
from ally.api.authentication import auth

# --------------------------------------------------------------------

@modelLiveDesk
class Blog(Entity):
    '''
    Provides the blog model.
    '''
    Language = LanguageEntity
    Creator = User; Creator = auth(Creator) # This is redundant, is just to keep IDE hinting.
    Title = str
    Description = str
    CreatedOn = datetime
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

# --------------------------------------------------------------------

#TODO: change the policy, here more of a security check this doesn't need to happen for authentification
# remove methods like getBlog, getAll
@service((Entity, Blog))
class IBlogService(IEntityCRUDService):
    '''
    Provides the service methods for the blogs.
    '''

    @call
    def getBlog(self, blogId:Blog, userId:auth(User)=None) -> Blog:
        '''
        Provides the blog based on the specified id, is the user is not specified the blog will be returned only if is
        in live mode.
        '''

    @call
    def getAll(self, languageId:LanguageEntity=None, adminId:auth(User)=None, offset:int=None, limit:int=None,
               detailed:bool=True, q:QBlog=None) -> Iter(Blog):
        '''
        Provides all the blogs.
        '''

    @call(webName='Administered')
    def getLiveWhereAdmin(self, adminId:auth(User), languageId:LanguageEntity=None, q:QBlog=None) -> Iter(Blog):
        '''
        Provides all the blogs that are administered by the provided user.
        '''

    @call(webName='Live')
    def getLive(self, languageId:LanguageEntity=None, q:QBlog=None) -> Iter(Blog):
        '''
        Provides all the blogs that are live at this moment.
        '''
