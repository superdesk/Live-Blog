'''
Created on Jan 8, 2014

@package: workflow
@copyright: 2013 Sourcefabric o.p.s.
@license: http://www.gnu.org/licenses/gpl-3.0.txt
@author: Gabriel Nistor

API specifications for node user association.
'''

from ally.api.config import service, call, DELETE
from ally.api.option import SliceAndTotal  # @UnusedImport
from ally.api.type import Iter
from superdesk.user.api.user import User

from .node import Node, QNode


# --------------------------------------------------------------------
# No model
# --------------------------------------------------------------------
# No query
# --------------------------------------------------------------------
@service
class INodeUserService:
    '''
    Provides the user node associations.
    '''
    
    @call
    def getDestinations(self, nodeId:Node, userId:User, q:QNode=None, **options:SliceAndTotal) -> Iter(Node.GUID):
        ''' Provides the possible destinations from the provided node based on the user node assignments.'''

    @call
    def addUser(self, nodeId:Node.GUID, userId: User.Id):
        ''' Adds a user to the provided node.'''
        
    @call(method=DELETE)
    def remUser(self, nodeId:Node, userId: User) -> bool:
        ''' Remove the user from the provided node.'''
