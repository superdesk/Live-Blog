'''
Created on Feb 11, 2013

@package: livedesk
@copyright: 2013 Sourcefabric o.p.s.
@license: http://www.gnu.org/licenses/gpl-3.0.txt
@author: Ioan v. Pocol

API specifications for livedesk blog collaborator group.
'''

from .blog import Blog
from ally.api.config import service, call, DELETE, UPDATE
from ally.api.type import Iter
from ally.support.api.entity import Entity
from datetime import datetime
from livedesk.api.blog_collaborator import BlogCollaborator
from livedesk.api.domain_livedesk import modelLiveDesk

# --------------------------------------------------------------------

@modelLiveDesk
class BlogCollaboratorGroup(Entity):
    '''
    Provides the blog collaborator group.
    '''
    Blog = Blog
    LastAccessOn = datetime
    
@modelLiveDesk
class BlogCollaboratorGroupMember(Entity):
    '''
    Provides the blog collaborator group member.
    '''
    Blog = BlogCollaboratorGroup
    BlogCollaborator = BlogCollaborator  

# --------------------------------------------------------------------

# TODO: review the API
@service
class IBlogCollaboratorGroupService:
    '''
    Provides the service methods for the blog collaborators group.
    '''
        
    @call
    def getById(self, groupId:BlogCollaboratorGroup.Id) -> BlogCollaboratorGroup:
        '''
        Provides the blog collaborator group by his id.
        '''
        
    @call
    def getAllMembers(self, groupId:BlogCollaboratorGroup.Id) -> Iter(BlogCollaboratorGroupMember):
        '''
        Provides all members of the blog collaborator group.
        '''

    @call
    def insert(self, collaboratorGroup:BlogCollaboratorGroup) -> BlogCollaboratorGroup.Id:
        '''
        Creates a new blog collaborator group and add to it as members all collaborators currently associated to the blog.
        '''

    @call
    def delete(self, groupId:BlogCollaboratorGroup.Id) -> bool:
        '''
        Deletes the blog collaborator group and all associated members
        '''

    @call(method=UPDATE)
    def addCollaborator(self, groupId:BlogCollaboratorGroup.Id, collaboratorId:BlogCollaborator.Id) -> bool:
        '''
        Assigns the collaborator as a member to the blog collaborator group.
        '''

    @call(method=DELETE)
    def removeCollaborator(self, groupId:BlogCollaboratorGroup.Id, collaboratorId:BlogCollaborator.Id) -> bool:
        '''
        Removes the collaborator from the member list of blog collaborator group.
        '''
