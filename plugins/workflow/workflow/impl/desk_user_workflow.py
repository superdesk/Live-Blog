'''
Created on Jan 20, 2014

@package: workflow
@copyright: 2013 Sourcefabric o.p.s.
@license: http://www.gnu.org/licenses/gpl-3.0.txt
@author: Mihai Gociu

Implementation for desk-user-workflow association service.
'''

from ally.container.ioc import injected
from ally.container.support import setup
from sql_alchemy.impl.entity import EntityServiceAlchemy
from sql_alchemy.support.util_service import iterateCollection
from sqlalchemy.orm.exc import NoResultFound
from workflow.api.desk_user_workflow import IDeskUserWorkflowService
from workflow.meta.desk import DeskMapped
from workflow.api.workflow import IWorkflowService
from workflow.meta.desk_user_workflow import DeskUserWorkflow
from ally.container import wire
from superdesk.user.meta.user import UserMapped
from ally.api.error import IdError

# --------------------------------------------------------------------

@injected
@setup(IDeskUserWorkflowService, name='deskUserWorkflowService')
class DeskUserWorkflowServiceAlchemy(EntityServiceAlchemy, IDeskUserWorkflowService):
    '''
    Implementation for @see: IDeskUserWorkflowService
    '''
    workflowService = IWorkflowService; wire.entity('workflowService')
    
    def __init__(self):
        EntityServiceAlchemy.__init__(self, DeskMapped)
    
    def getWorkflows(self, desk, user=None, **options):
        '''
        @see: IDeskUserWorkflowService.getWorkflows
        '''
        #get the id of the desk
        try: deskId, = self.session().query(DeskMapped.id).filter(DeskMapped.Name == desk).one()
        except NoResultFound: return None
        
        sql = self.session().query(DeskUserWorkflow.Workflow)
        sql = sql.filter(DeskUserWorkflow.desk == deskId)
        if user: sql = sql.filter(DeskUserWorkflow.user == user)
        return iterateCollection(sql)
    
    def getUsers(self, desk, workflow=None, **options):
        ''' 
        @see: IDeskUserWorkflowService.getUsers
        '''
        #get the id of the desk
        try: deskId, = self.session().query(DeskMapped.id).filter(DeskMapped.Name == desk).one()
        except NoResultFound: return None
        
        sql = self.session().query(DeskUserWorkflow.user)
        sql = sql.filter(DeskUserWorkflow.desk == deskId)
        if workflow: sql = sql.filter(DeskUserWorkflow.Workflow == workflow)
        return iterateCollection(sql)
        
    def getDesks(self, user, **options):
        ''' 
        @see: IDeskUserWorkflowService.getDesks
        '''
        sql = self.session().query(DeskMapped.Name).join(DeskUserWorkflow, DeskUserWorkflow.desk == DeskMapped.id)
        sql = sql.filter(DeskUserWorkflow.user == user)
        return iterateCollection(sql)
        
    def addDeskUserWorkflow(self, desk, workflow, user):
        '''
        @see: IDeskUserWorkflowService.addDeskUserWorkflow
        '''
        #first make sure the desk, user and workflow exist
        try:
            deskId, = self.session().query(DeskMapped.id).filter(DeskMapped.Name == desk).one()
            userId, = self.session().query(UserMapped.Id).filter(UserMapped.Id == user).one()
            self.workflowService.getById(workflow)
        except NoResultFound: return False
        except IdError: return False
        
        #check if the desk-user-workflow has already been added
        sql = self.session().query(DeskUserWorkflow).filter((DeskUserWorkflow.desk == deskId) & (DeskUserWorkflow.user == userId) & 
                                                            (DeskUserWorkflow.Workflow == workflow))
        if sql.count() == 0:
            association = DeskUserWorkflow(desk=deskId, user=userId, Workflow=workflow)
            self.session().add(association)
            return True
        return False
    
    def remDeskUserWorkflow(self, desk, workflow, user):
        '''
        @see: IDeskUserWorkflowService.remDeskUserWorkflow
        '''
        sql = self.session().query(DeskUserWorkflow).join(DeskMapped, DeskMapped.id == DeskUserWorkflow.desk)
        sql = sql.filter((DeskMapped.Name == desk) & (UserMapped.Id == user) & (DeskUserWorkflow.Workflow == workflow))
        
        try: assoc = sql.one()
        except NoResultFound: return False
        self.session().delete(assoc)
        return True
    
    