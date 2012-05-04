'''
Created on May 4, 2012

@package: livedesk
@copyright: 2012 Sourcefabric o.p.s.
@license: http://www.gnu.org/licenses/gpl-3.0.txt
@author: Gabriel Nistor

API specifications for livedesk blog collaborator.
'''

from .blog import Blog
from ally.api.config import service, call, INSERT, DELETE
from ally.api.type import Iter
from ally.support.api.entity import Entity, IEntityGetService
from livedesk.api.domain_livedesk import modelLiveDesk
from superdesk.collaborator.api.collaborator import Collaborator

# --------------------------------------------------------------------

@modelLiveDesk
class BlogCollaborator(Entity):
    '''
    Provides the blog collaborator model.
    '''
    Blog = Blog
    Collaborator = Collaborator

# --------------------------------------------------------------------

# No query

# --------------------------------------------------------------------

@service((Entity, BlogCollaborator))
class IBlogCollaboratorService(IEntityGetService):
    '''
    Provides the service methods for the blog collaborators.
    '''

    @call
    def getAll(self, blogId:Blog.Id=None, collaboratorId:Collaborator.Id=None,
               offset:int=None, limit:int=None) -> Iter(BlogCollaborator):
        '''
        Provides all the blog collaborators.
        '''

    @call(method=INSERT)
    def addCollaborator(self, blogId:Blog.Id, collaboratorId:Collaborator.Id) -> BlogCollaborator.Id:
        '''
        Assigns the collaborator as a collaborator to the blog.
        '''

    @call(method=DELETE)
    def removeCollaborator(self, blogId:Blog.Id, collaboratorId:Collaborator.Id) -> bool:
        '''
        Removes the collaborator from the blog.
        '''

    @call
    def remove(self, blogCollaboratorId:BlogCollaborator.Id) -> bool:
        '''
        Removes the blog collaborator.
        '''
