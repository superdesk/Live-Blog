'''
Created on Jan 17, 2014

@package: workflow
@copyright: 2013 Sourcefabric o.p.s.
@license: http://www.gnu.org/licenses/gpl-3.0.txt
@author: Mihai Gociu

API specifications for work flows.
'''

from ally.api.config import service
from ally.support.api.entity_named import IEntityGetService, IEntityFindService, Entity
from workflow.api.domain_workflow import modelWorkFlow

# --------------------------------------------------------------------

@modelWorkFlow
class Workflow(Entity):
    '''
    Provides the workflow model.
    '''
    Name = str
    
    def __init__(self, Name=None):
        ''' Construct the workflow with the provided name.'''
        if Name is not None: self.Name = Name
    
# --------------------------------------------------------------------

@service((Entity, Workflow))
class IWorkflowService(IEntityGetService, IEntityFindService):
    '''
    '''
    
        
