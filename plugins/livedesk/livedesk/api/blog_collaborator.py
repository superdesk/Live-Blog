'''
Created on May 4, 2012

@package: livedesk
@copyright: 2012 Sourcefabric o.p.s.
@license: http://www.gnu.org/licenses/gpl-3.0.txt
@author: Gabriel Nistor

API specifications for livedesk blog collaborator.
'''

from .blog import Blog
from ally.api.config import service, call, DELETE, UPDATE
from ally.api.type import Iter
from livedesk.api.domain_livedesk import modelLiveDesk
from superdesk.collaborator.api.collaborator import Collaborator
from superdesk.source.api.source import QSource
from superdesk.user.api.user import QUser, User
from gui.action.api.action import Action
from ally.api.option import SliceAndTotal  # @UnusedImport
from .blog_collaborator_type import BlogCollaboratorType

# --------------------------------------------------------------------

@modelLiveDesk(name=Collaborator)
class BlogCollaborator(Collaborator):
    '''
    Provides the blog collaborator model.
    '''
    Blog = Blog
    Type = BlogCollaboratorType

# --------------------------------------------------------------------

# No query

# --------------------------------------------------------------------

@service
class IBlogCollaboratorService:
    '''
    Provides the service methods for the blog collaborators.
    '''

    # TODO: refactor: At a latter stage try to remove the blogId from this method since that info is already captured
    # in the collaborator id, probably this was done this way for filters, but we can have a specific collaborator filter
    # rather then have the blog id.
    @call
    def getById(self, blogId:Blog, collaboratorId:BlogCollaborator) -> BlogCollaborator:
        '''
        Provides the blog collaborator based on the id.
        '''
    
    @call(webName='All')
    def getActions(self, userId:User.Id, blogId:Blog, **options:SliceAndTotal) -> Iter(Action.Path):
        '''
        Get all actions registered for the provided user for the blog.
        '''
    
    @call
    def getActionsRoot(self, userId:User.Id, blogId:Blog, **options:SliceAndTotal) -> Iter(Action.Path):
        '''
        Get root actions registered for the provided user for the blog.
        '''
        
    @call(webName='Sub')
    def getSubActions(self, userId:User.Id, blogId:Blog, parentPath:Action.Path, **options:SliceAndTotal) -> Iter(Action.Path):
        '''
        Get sub actions of the action path registered for the provided user for the blog.
        '''

    @call
    def getAll(self, blogId:Blog, **options:SliceAndTotal) -> Iter(BlogCollaborator.Id):
        '''
        Provides all the blog collaborators.
        '''

    @call(webName="Potential")
    def getPotential(self, blogId:Blog, excludeSources:bool=True, qu:QUser=None, qs:QSource=None,
                     **options:SliceAndTotal) -> Iter(Collaborator.Id):
        '''
        Provides all the collaborators that are not registered to this blog.
        '''

    @call(method=UPDATE)
    def addCollaborator(self, blogId:Blog.Id, collaboratorId:Collaborator.Id, typeName:BlogCollaboratorType.Name):
        '''
        Assigns the collaborator as a collaborator to the blog.
        '''
    # TODO: merge this methods when will do the combinations for UPDATE.
    @call(method=UPDATE, webName='Add')
    def addCollaboratorAsDefault(self, blogId:Blog.Id, collaboratorId:Collaborator.Id):
        '''
        Assigns the collaborator as a collaborator to the blog.
        '''

    @call(method=DELETE, webName='Remove')
    def removeCollaborator(self, blogId:Blog, collaboratorId:Collaborator) -> bool:
        '''
        Removes the collaborator from the blog.
        '''
