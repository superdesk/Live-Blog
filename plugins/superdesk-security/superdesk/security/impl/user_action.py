'''
Created on Feb 27, 2012

@package: superdesk security
@copyright 2011 Sourcefabric o.p.s.
@license http://www.gnu.org/licenses/gpl-3.0.txt
@author: Gabriel Nistor

Action manager implementation for user GUI actions. 
'''

from acl.impl.action_right import TypeAction, RightAction
from ally.container import wire
from ally.container.ioc import injected
from ally.container.support import setup
from ally.exception import InputError
from gui.action.api.action import IActionManagerService, Action
from gui.action.impl.action import processChildCount
from security.acl.core.spec import IAclAccessService
from security.api.right_type import IRightTypeService, RightType
from superdesk.security.api.user_action import IUserActionService
from superdesk.security.api.user_rbac import IUserRbacService

# --------------------------------------------------------------------

@injected
@setup(IUserActionService, name='userActionService')
class IUserActionServiceAlchemy(IUserActionService):
    '''
    Provides the implementation user GUI actions @see: IUserActionService.
    '''
    
    actionManagerService = IActionManagerService; wire.entity('actionManagerService')
    # The action manager that provides all the applications actions.
    aclAccessService = IAclAccessService; wire.entity('aclAccessService')
    # The acl access service.
    userRbacService = IUserRbacService; wire.entity('userRbacService')
    # The user rbac service.
    rightTypeService = IRightTypeService; wire.entity('rightTypeService')
    # The right type service.
    aclType = TypeAction; wire.entity('aclType')
    # The GUI acl type.
    
    def __init__(self):
        assert isinstance(self.actionManagerService, IActionManagerService), \
        'Invalid action manager service %s' % self.actionManagerService
        assert isinstance(self.aclAccessService, IAclAccessService), 'Invalid acl access service %s' % self.aclAccessService
        assert isinstance(self.userRbacService, IUserRbacService), 'Invalid user rbac service %s' % self.userRbacService
        assert isinstance(self.rightTypeService, IRightTypeService), 'Invalid right type service %s' % self.rightTypeService
        assert isinstance(self.aclType, TypeAction), 'Invalid acl action type %s' % self.aclType

    def getAll(self, userId, path=None):
        '''
        @see: IUserActionService.getAll
        '''
        try: rightType = self.rightTypeService.getByName(self.aclType.name)
        except InputError: return ()
        assert isinstance(rightType, RightType)
        actionPaths = set()
        rights = (right.Name for right in self.userRbacService.getRights(userId, rightType.Id))
        for aclRight in self.aclAccessService.rightsFor(rights, typeName=self.aclType.name):
            if isinstance(aclRight, RightAction):
                assert isinstance(aclRight, RightAction)
                for action in aclRight.actions():
                    assert isinstance(action, Action)
                    actionPaths.add(action.Path)
        
        actions = []
        for action in self.actionManagerService.getAll(path):
            if action.Path in actionPaths: actions.append(action)
        return processChildCount(actions)
