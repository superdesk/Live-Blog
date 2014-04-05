'''
Created on Jan 27, 2014

@package: workflow
@copyright: 2011 Sourcefabric o.p.s.
@license http://www.gnu.org/licenses/gpl-3.0.txt
@author: Mihai Gociu

Implementation for assignment service.

'''
from ally.container.ioc import injected
from ally.container.support import setup
from sql_alchemy.impl.entity import EntityServiceAlchemy
from ally.api.validate import validate
from sqlalchemy.orm.exc import NoResultFound
from workflow.api.assignment import IAssignmentService, QAssignment, Assignment
from workflow.meta.assignment import AssignmentMapped, NodeDB
from ally.container import wire
from workflow.api.nodes import INodesService
from uuid import uuid4

# --------------------------------------------------------------------

@injected
@setup(IAssignmentService, name='assignmentService')
@validate(AssignmentMapped)
class AssignmentServiceAlchemy(EntityServiceAlchemy, IAssignmentService):
    '''
    Implementation for @see: IAssignmentService
    '''
    nodesService = INodesService; wire.entity('nodesService')
    
    def __init__(self):
        EntityServiceAlchemy.__init__(self, AssignmentMapped, QAssignment)
    
    def insert(self, entity):
        '''
        @see: IAssignmentService.insert 
        '''
        assert isinstance(entity, Assignment), 'Invalid assignement %s' % entity
        entity.GUID = uuid4().hex
        super().insert(entity)
        self.updateAssignmentNode(entity)
        return entity.GUID
    
    def update(self, entity):
        '''
        @see: IAssignmentService.update 
        '''
        assert isinstance(entity, Assignment), 'Invalid assignement %s' % entity
        super().update(entity)
        self.updateAssignmentNode(entity)
    
    def getAssignments(self, node, q, **options):
        '''
        @see: IAssignmentService.getAssignments
        '''
        sql = self.session().query(AssignmentMapped)
        if node: 
            sql.filter(AssignmentMapped.nodeId == self.nodeId(node))
        
        if q:
            assert isinstance(q, QAssignment), 'Invalid query %s' % q
            if q.name:
                sql = sql.filter(AssignmentMapped.Name == q.name)
        
        assignments = []
        for mapped in sql.all():
            assignment = Assignment()
            assignment.Name = mapped.Name
            assignment.Description = mapped.Description
            assignment.Node = node
            assignments.append(mapped)
        
        return assignments

    # ----------------------------------------------------------------
    #TODO: integrate this method into getAssignments
    def getUnassignedAssignments(self):
        '''
        @see: IAssignmentService.getUnassignedAssignments
        '''
        #get the assignments with invalid node or with no node
        sql = self.session().query(AssignmentMapped, NodeDB.GUID).outerjoin(NodeDB, NodeDB.id == AssignmentMapped.Node)
        return [assignment for assignment, node in sql.all() if not self.nodesService.getNode(node)]
    
    def updateAssignmentNode(self, entity):
        if Assignment.Node in entity:
            if not self.nodesService.getNode(entity.Node): return #inexistent node
            if entity.Node is None: nodeId = None
            else:
                self.addNodeToDB(entity.Node)
                nodeId = self.nodeId(entity.Node)
            self.session().query(AssignmentMapped).filter(AssignmentMapped.GUID == entity.GUID).update({AssignmentMapped.nodeId: nodeId})
    
    def addNodeToDB(self, guid):
        #add the node to database, if it is not already there
        try:
            self.session().query(NodeDB.id).filter(NodeDB.GUID == guid).one()
        except NoResultFound:
            nodeDB = NodeDB()
            nodeDB.GUID = guid
            self.session().add(nodeDB)
    
    def nodeId(self, guid):
        ''' Provides the database node id for the provided GUID.'''
        try: return self.session().query(NodeDB.id).filter(NodeDB.GUID == guid).one()
        except NoResultFound: return
    
    def removeNodeFromDB(self, node):
        #do some cleanup on the database: delete the node from the database
        try:
            nodeDB = self.session().query(NodeDB).filter(NodeDB.GUID == node).one()
        except NoResultFound: return
        self.session().delete(nodeDB)
        
    