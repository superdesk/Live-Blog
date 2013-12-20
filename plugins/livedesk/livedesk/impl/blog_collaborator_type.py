'''
Created on Dec 20, 2013

@package: livedesk
@copyright: 2012 Sourcefabric o.p.s.
@license: http://www.gnu.org/licenses/gpl-3.0.txt
@author: Gabriel Nistor

Contains the implementation of the blog collaborator type API.
'''

from ally.api.validate import validate
from ally.container.ioc import injected
from ally.container.support import setup
from gui.action.core.impl.category import ActionCategoryServiceAlchemy
from livedesk.api.blog_collaborator_type import IBlogCollaboratorTypeService, \
    IBlogCollaboratorTypeActionService, BlogCollaboratorType
from livedesk.meta.blog_collaborator_type import BlogCollaboratorTypeMapped, \
    BlogCollaboratorTypeAction
from sql_alchemy.impl.entity import EntityNQServiceAlchemy, EntitySupportAlchemy


# --------------------------------------------------------------------
@injected
@setup(IBlogCollaboratorTypeService, name='blogCollaboratorTypeService')
@validate(BlogCollaboratorTypeMapped)
class BlogCollaboratorTypeServiceAlchemy(EntityNQServiceAlchemy, IBlogCollaboratorTypeService):
    '''
    Implementation for @see: IBlogCollaboratorTypeService
    '''

    def __init__(self):
        '''
        Construct the blog collaborator type service.
        '''
        EntitySupportAlchemy.__init__(self, BlogCollaboratorTypeMapped)
        
    def insert(self, entity):
        '''
        @see: IBlogCollaboratorTypeService.insert
        '''
        assert isinstance(entity, BlogCollaboratorType), 'Invalid collaborator type %s' % entity
        if entity.IsDefault:
            sql = self.session().query(BlogCollaboratorTypeMapped)
            sql.update({BlogCollaboratorTypeMapped.IsDefault: False}, False)
        return super().insert(entity)
    
    def update(self, entity):
        '''
        @see: IBlogCollaboratorTypeService.update
        '''
        assert isinstance(entity, BlogCollaboratorType), 'Invalid collaborator type %s' % entity
        if entity.IsDefault:
            sql = self.session().query(BlogCollaboratorTypeMapped)
            sql.update({BlogCollaboratorTypeMapped.IsDefault: False}, False)
        return super().update(entity)
        
# --------------------------------------------------------------------

@injected
@setup(IBlogCollaboratorTypeActionService, name='blogCollaboratorTypeActionService')
class BlogCollaboratorTypeActionServiceAlchemy(ActionCategoryServiceAlchemy, IBlogCollaboratorTypeActionService):
    '''
    Implementation for @see: IBlogCollaboratorTypeActionService
    '''

    def __init__(self):
        '''
        Construct the blog collaborator type to action service.
        '''
        ActionCategoryServiceAlchemy.__init__(self, BlogCollaboratorTypeMapped, BlogCollaboratorTypeAction)
