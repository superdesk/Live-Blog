'''
Created on May 2, 2012

@package: superdesk collaborator
@copyright: 2012 Sourcefabric o.p.s.
@license: http://www.gnu.org/licenses/gpl-3.0.txt
@author: Gabriel Nistor

API specifications for collaborators.
'''

from ally.api.config import service, call, LIMIT_DEFAULT
from ally.api.type import Iter
from ally.support.api.entity import Entity, IEntityGetCRUDService
from superdesk.api.domain_superdesk import modelData
from superdesk.source.api.source import Source, QSource
from superdesk.user.api.user import User, QUser
from superdesk.user.meta.user import UserMapped

# --------------------------------------------------------------------

@modelData
class Collaborator(Entity):
    '''
    Provides the collaborator model.
    '''
    User = User
    Source = Source
    Name = str

# --------------------------------------------------------------------

# No query

# --------------------------------------------------------------------

@service((Entity, Collaborator))
class ICollaboratorService(IEntityGetCRUDService):
    '''
    Provides the service methods for the collaborators.
    '''

    @call
    def getAll(self, userId:UserMapped.Id=None, sourceId:Source.Id=None, offset:int=None, limit:int=LIMIT_DEFAULT,
               detailed:bool=True, qu:QUser=None, qs:QSource=None) -> Iter(Collaborator):
        '''
        Provides all the collaborators.
        '''

