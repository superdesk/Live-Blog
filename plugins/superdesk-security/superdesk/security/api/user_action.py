'''
Created on Feb 27, 2012

@package: superdesk security
@copyright 2011 Sourcefabric o.p.s.
@license http://www.gnu.org/licenses/gpl-3.0.txt
@author: Gabriel Nistor

Action manager interface for user GUI actions. 
'''

from ally.api.config import service, call
from ally.api.type import Iter
from gui.action.api.action import Action
from superdesk.user.api.user import User

# --------------------------------------------------------------------

@service
class IUserActionService:
    '''
    Provides the user GUI actions service.
    '''

    @call
    def getAll(self, userId:User.Id, path:str=None) -> Iter(Action):
        '''
        Get all actions registered for the provided user.
        '''
