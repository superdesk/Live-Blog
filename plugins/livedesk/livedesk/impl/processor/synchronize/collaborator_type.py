'''
Created on Dec 23, 2013

@package: livedesk
@copyright: 2011 Sourcefabric o.p.s.
@license: http://www.gnu.org/licenses/gpl-3.0.txt
@author: Mihai Gociu

Provides the synchronization with the database for livedesk blog collaborator types.
'''

from ally.container import wire
from ally.container.ioc import injected
from ally.container.support import setup
from ally.design.processor.attribute import requires
from ally.design.processor.context import Context
from ally.design.processor.execution import Chain
from ally.design.processor.handler import HandlerProcessor, Handler
from ally.support.util_context import listBFS
import logging
from livedesk.api.blog_collaborator_type import IBlogCollaboratorTypeService,\
    BlogCollaboratorType

# --------------------------------------------------------------------

log = logging.getLogger(__name__)

# --------------------------------------------------------------------

class Solicit(Context):
    '''
    The solicit context.
    '''
    # ---------------------------------------------------------------- Required
    repository = requires(Context)

class Repository(Context):
    '''
    The repository context.
    '''
    # ---------------------------------------------------------------- Required
    userType = requires(str)
    children = requires(list)
    actions = requires(list)

# --------------------------------------------------------------------

@injected
@setup(Handler, name='syncCollaboratorType')
class SyncCollaboratorType(HandlerProcessor):
    '''
    Implementation for a processor that synchronizes the blog collaborator types in the configuration file with the database.
    '''
    
    blogCollaboratorTypeService = IBlogCollaboratorTypeService; wire.entity('blogCollaboratorTypeService')
    
    def __init__(self):
        assert isinstance(self.blogCollaboratorTypeService, IBlogCollaboratorTypeService), \
        'Invalid blog collaborator service %s' % self.blogCollaboratorTypeService
        super().__init__(Repository=Repository)
        
    def process(self, chain, solicit:Solicit, **keyargs):
        '''
        @see: HandlerProcessor.process
        
        Synchronize the blog collaborator types in the configuration file with the ones in the database.
        '''
        assert isinstance(chain, Chain), 'Invalid chain %s' % chain
        assert isinstance(solicit, Solicit), 'Invalid solicit %s' % solicit
        assert isinstance(solicit.repository, Repository), 'Invalid repository %s' % solicit.repository
        
        typesFromConfig = {type.userType:type for type in listBFS(solicit.repository, Repository.children, Repository.userType)} 
        typesFromDb = set(self.blogCollaboratorTypeService.getAll())
        
        toAdd = set(type for type in typesFromConfig if type not in typesFromDb)
        toDelete = set(type for type in typesFromDb if type not in typesFromConfig)
        toUpdate = set(type for type in typesFromConfig if type in typesFromDb)
        
        for type in toAdd:
            entity = self.createCollaboratorTypeEntity(type, False)
            try:
                self.blogCollaboratorTypeService.insert(entity)
            except Exception as e:
                log.warning('Error adding Blog Collaborator Type \'%s\' to database', entity)
                log.warning(e)
        
        for type in toDelete:
            try:
                self.blogCollaboratorTypeService.delete(type)
            except Exception as e:
                log.warning('Error deleting Blog Collaborator Type \'%s\' from database', type)
                log.warning(e)
        
        for type in toUpdate:
            entity = self.createCollaboratorTypeEntity(type, False)
            try:
                self.blogCollaboratorTypeService.update(entity)
            except Exception as e:
                log.warning('Error updating Blog Collaborator Type \'%s\' to database', entity)
                log.warning(e)
    
    def createCollaboratorTypeEntity(self, typeName, isDefault):    
        entity = BlogCollaboratorType()
        entity.Name = typeName
        entity.IsDefault = isDefault
        return entity
