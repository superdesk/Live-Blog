'''
Created on May 2, 2012

@package: superdesk collaborator
@copyright: 2012 Sourcefabric o.p.s.
@license: http://www.gnu.org/licenses/gpl-3.0.txt
@author: Gabriel Nistor

API specifications for collaborators.
'''

from ally.api.config import service, call
from ally.api.type import Iter
from superdesk.api.domain_superdesk import modelData
from superdesk.source.api.source import Source, QSource
from superdesk.user.api.user import User, QUser
from ally.support.api.entity_ided import Entity, IEntityGetCRUDService
from ally.api.option import SliceAndTotal # @UnusedImport

# --------------------------------------------------------------------

@modelData
class Collaborator(Entity):
    '''Provides the collaborator model.'''
    User = User
    Source = Source
    Name = str

# --------------------------------------------------------------------

# No query

# --------------------------------------------------------------------

@service((Entity, Collaborator))
class ICollaboratorService(IEntityGetCRUDService):
    '''Provides the service methods for the collaborators.'''

    @call
    def getAll(self, userId:User.Id=None, sourceId:Source.Id=None, qu:QUser=None,
               qs:QSource=None, **options:SliceAndTotal) -> Iter(Collaborator.Id):
        '''Provides all the collaborators.'''

