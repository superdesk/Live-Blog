'''
Created on Feb 27, 2012

@package: superdesk security
@copyright 2011 Sourcefabric o.p.s.
@license http://www.gnu.org/licenses/gpl-3.0.txt
@author: Gabriel Nistor

Action manager implementation for user GUI actions. 
'''

from acl.right_action import RightAction
from acl.spec import TypeAcl
from ally.container import wire
from ally.container.ioc import injected
from ally.container.support import setup
from ally.design.processor.assembly import Assembly
from ally.design.processor.attribute import defines, requires
from ally.design.processor.context import Context
from ally.design.processor.execution import Processing, Chain
from collections import Iterable
from gui.action.api.action import IActionManagerService, Action
from gui.action.impl.action import processChildCount
from superdesk.security.api.user_action import IUserActionService

# --------------------------------------------------------------------

class Solicitation(Context):
    '''
    The solicitation context.
    '''
    # ---------------------------------------------------------------- Defined
    userId = defines(int, doc='''
    @rtype: integer
    The id of the user to create gateways for.
    ''')
    types = defines(Iterable, doc='''
    @rtype: Iterable(TypeAcl)
    The ACL types to create gateways for.
    ''')

class Reply(Context):
    '''
    The reply context.
    '''
    # ---------------------------------------------------------------- Required
    rightsAvailable = requires(Iterable, doc='''
    @rtype: Iterable(RightAcl)
    The rights that are available.
    ''')
    
# --------------------------------------------------------------------

@injected
@setup(IUserActionService, name='userActionService')
class IUserActionServiceAlchemy(IUserActionService):
    '''
    Provides the implementation user GUI actions @see: IUserActionService.
    '''
    
    actionManagerService = IActionManagerService; wire.entity('actionManagerService')
    # The action manager that provides all the applications actions.
    actionType = TypeAcl; wire.entity('actionType')
    # The GUI acl action type.
    assemblyActiveRights = Assembly; wire.entity('assemblyActiveRights')
    # The assembly to be used for getting the active rights.
    
    def __init__(self):
        assert isinstance(self.actionManagerService, IActionManagerService), \
        'Invalid action manager service %s' % self.actionManagerService
        assert isinstance(self.actionType, TypeAcl), 'Invalid acl action type %s' % self.actionType
        assert isinstance(self.assemblyActiveRights, Assembly), 'Invalid assembly rights %s' % self.assemblyActiveRights
        
        self._processing = self.assemblyActiveRights.create(solicitation=Solicitation, reply=Reply)

    def getAll(self, userId, path=None):
        '''
        @see: IUserActionService.getAll
        '''
        assert isinstance(userId, int), 'Invalid user id %s' % userId
        
        proc = self._processing
        assert isinstance(proc, Processing), 'Invalid processing %s' % proc
        
        solicitation = proc.ctx.solicitation()
        assert isinstance(solicitation, Solicitation), 'Invalid solicitation %s' % solicitation
        solicitation.userId = userId
        solicitation.types = (self.actionType,)
        
        chain = Chain(proc)
        chain.process(solicitation=solicitation, reply=proc.ctx.reply()).doAll()
        
        reply = chain.arg.reply
        assert isinstance(reply, Reply), 'Invalid reply %s' % reply
        if Reply.rightsAvailable not in reply: return ()
        
        actionPaths = set()
        for aclRight in reply.rightsAvailable:
            if isinstance(aclRight, RightAction):
                assert isinstance(aclRight, RightAction)
                for action in aclRight.actions():
                    assert isinstance(action, Action)
                    intermPath = []
                    for item in action.Path.split('.'):
                        intermPath.append(item)
                        actionPaths.add('.'.join(intermPath))
        
        actions = []
        for action in self.actionManagerService.getAll(path):
            if action.Path in actionPaths: actions.append(action)
        return processChildCount(actions)
