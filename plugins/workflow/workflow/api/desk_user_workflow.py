'''
Created on Jan 20, 2014

@package: workflow
@copyright: 2013 Sourcefabric o.p.s.
@license: http://www.gnu.org/licenses/gpl-3.0.txt
@author: Mihai Gociu

API specifications for desk-user-workflow association service.
'''

from ally.api.config import service, call, DELETE
from ally.api.option import SliceAndTotal  # @UnusedImport
from ally.api.type import Iter
from workflow.api.desk import Desk
from superdesk.user.api.user import User
from workflow.api.workflow import Workflow

# --------------------------------------------------------------------

# No model

# --------------------------------------------------------------------

# No query
    
# --------------------------------------------------------------------

@service
class IDeskUserWorkflowService:
    '''
    '''
    
    @call
    def getWorkflows(self, desk:Desk.Name, user:User.Id=None, **options:SliceAndTotal) -> Iter(Workflow.Name):
        ''' '''
        
    @call
    def getUsers(self, desk:Desk.Name, workflow:Workflow.Name=None, **options:SliceAndTotal) -> Iter(User.Id):
        ''' '''
        
    @call
    def getDesks(self, user:User.Id, **options:SliceAndTotal) -> Iter(Desk.Name):
        ''' '''
    
    @call
    def addDeskUserWorkflow(self, desk:Desk.Name, workflow:Workflow.Name, user:User.Id, ) -> bool:
        ''' '''
        
    @call(method=DELETE)
    def remDeskUserWorkflow(self, desk:Desk.Name, workflow:Workflow.Name, user:User.Id) -> bool:
        ''' '''
    
