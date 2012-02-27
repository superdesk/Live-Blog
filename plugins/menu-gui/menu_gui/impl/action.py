from menu_gui.api.action import IActionManagerService, Action
from ally.container.ioc import injected
from ally.exception import InputException, Ref
from ally.internationalization import translator

# --------------------------------------------------------------------

_ = translator(__name__)

# --------------------------------------------------------------------

@injected
class ActionManagerService(IActionManagerService):
    '''
    @see: IActionManagerService
    '''

    def __init__(self):
        '''  '''
        self._actionList = {}
        self._id = 0
    
    def add(self, action):
        '''
        @see: IActionManagerService.add
        '''
        assert isinstance(action, Action), 'Invalid parameter action: %s' % action
        self._id = self._id+1
        action.Id = self._id
        self._actionList[action.Id] = action
        
    def getById(self, id):
        '''
        '''
        if id not in self._actionList:
            raise InputException(Ref(_('Invalid id'), ref=Action.Id))
        return self._actionList[id]
        
    def getAll(self):
        '''
        @see: IActionManagerService.getAll
        '''
        return self._actionList.values() 
    
    def getByParent(self, parentId):
        '''
        @see: IActionManagerService.getByParent
        '''
        return (action for action in self._actionList.values() if action.Parent == parentId)
    