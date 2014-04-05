'''
Created on Jan 20, 2014

@author: mihaigociu

@package: workflow
@copyright: 2013 Sourcefabric o.p.s.
@license: http://www.gnu.org/licenses/gpl-3.0.txt
@author: Mihai Gociu

Implementation for work flows.

'''

from ally.api.error import IdError
from ally.container import wire
from ally.container.ioc import injected
from ally.container.support import setup
from ally.support.api.util_service import trimIter
from ally.api.option import SliceAndTotal # @UnusedImport
from workflow.api.workflow import IWorkflowService, Workflow


# --------------------------------------------------------------------
@injected
@setup(IWorkflowService, name='workflowService')
class WorkflowService(IWorkflowService):
    '''
    Implementation for @see: IWorkflowService
    '''
    
    workflows = list; wire.entity('workflows')
    
    def __init__(self):
        assert isinstance(self.workflows, list), 'Invalid workflows %s' % self.workflows
    
    def getById(self, identifier):
        '''
        @see: IWorkflowService.getById
        '''
        if identifier not in self.workflows: raise IdError()
        return Workflow(Name=identifier)
        
    def getAll(self, **options:SliceAndTotal):
        '''
        @see: IWorkflowService.getAll
        '''
        if 'withTotal' in options: options.pop('withTotal')
        return trimIter(self.workflows, len(self.workflows), **options)

