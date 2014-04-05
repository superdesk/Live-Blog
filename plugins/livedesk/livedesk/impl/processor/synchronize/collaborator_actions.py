'''
Created on Jan 7, 2014

@package: livedesk
@copyright: 2011 Sourcefabric o.p.s.
@license: http://www.gnu.org/licenses/gpl-3.0.txt
@author: Mihai Gociu

Provides the synchronization with the database for livedesk blog collaborator actions.

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
from livedesk.api.blog_collaborator_type import IBlogCollaboratorTypeActionService

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

class Action(Context):
        '''
        The action container context.
        '''
        # ---------------------------------------------------------------- Required
        path = requires(str)
        label = requires(str)
        script = requires(str)
        navBar = requires(str)

# --------------------------------------------------------------------

@injected
@setup(Handler, name='syncCollaboratorActions')
class SyncCollaboratorActions(HandlerProcessor):
    '''
    Implementation for a processor that synchronizes the blog collaborator actions in the configuration file with the database.
    '''
    
    blogCollaboratorTypeActionService = IBlogCollaboratorTypeActionService; wire.entity('blogCollaboratorTypeActionService')

    def __init__(self):
        assert isinstance(self.blogCollaboratorTypeActionService, IBlogCollaboratorTypeActionService), \
        'Invalid blog collaborator service %s' % self.blogCollaboratorTypeActionService
        super().__init__(Repository=Repository, Action=Action)

    def process(self, chain, solicit:Solicit, **keyargs):
        '''
        @see: HandlerProcessor.process
        
        Synchronize the blog collaborator actions in the configuration file with the ones in in the database.
        '''
        assert isinstance(chain, Chain), 'Invalid chain %s' % chain
        assert isinstance(solicit, Solicit), 'Invalid solicit %s' % solicit
        assert isinstance(solicit.repository, Repository), 'Invalid repository %s' % solicit.repository
        
        typesFromConfig = listBFS(solicit.repository, Repository.children, Repository.userType)
        for repository in typesFromConfig:
            #sync actions for each collaborator type with the database
            assert isinstance(repository, Repository), 'Invalid repository %s' % type
            repository.userType
            
            actionsFromConfig = set(action.path for action in repository.actions)
            actionsFromDb = set(self.blogCollaboratorTypeActionService.getActions(repository.userType))
            
            toAdd = actionsFromConfig.difference(actionsFromDb)
            toDelete = actionsFromDb.difference(actionsFromConfig)
            
            for action in toAdd:
                try:
                    self.blogCollaboratorTypeActionService.addAction(repository.userType, action)
                except Exception as e:
                    log.warning('Error adding Action \'%s\ to Blog Collaborator Type \'%s\' ', action, repository.userType)
                    log.warning(e)
            
            for action in toDelete:
                try:
                    self.blogCollaboratorTypeActionService.remAction(repository.userType, action)
                except Exception as e:
                    log.warning('Error deleting Action \'%s\ from Blog Collaborator Type \'%s\' ', action, repository.userType)
                    log.warning(e)
