'''
Created on Jan 12, 2013

@package: livedesk
@copyright: 2012 Sourcefabric o.p.s.
@license: http://www.gnu.org/licenses/gpl-3.0.txt
@author: Gabriel Nistor

The implementation for the blog filter.
'''

from ally.container import wire
from ally.container.support import setup
from ally.support.sqlalchemy.session import SessionSupport
from livedesk.api.filter_blog import IBlogAdminFilterService, \
    IBlogCollaboratorFilterService
from livedesk.meta.blog import BlogMapped
from livedesk.meta.blog_collaborator import BlogCollaboratorMapped, \
    BlogCollaboratorTypeMapped
from sqlalchemy.sql.expression import exists
from superdesk.collaborator.meta.collaborator import CollaboratorMapped

# --------------------------------------------------------------------

class BlogFilterServiceAlchemyBase(SessionSupport):
    '''
    Generic implementation for blog filter service.
    '''
    
    collaborator_types = []; wire.config('collaborator_types', doc='''
    The collaborator type name associated with this filter.
    ''')
    
    def __init__(self):
        assert isinstance(self.collaborator_types, list), 'Invalid collaborator types %s' % self.collaborator_types
        super().__init__()
    
    def isAllowed(self, userId, blogId):
        '''
        @see: IBlogAdminFilterService.isAllowed
        '''
        return self.session().query(BlogMapped).filter(self._createFilter(userId)).filter(BlogMapped.Id == blogId).count() > 0
    
    # ----------------------------------------------------------------
    
    def _createFilter(self, userId):
        '''
        Creates the filter for the query.
        '''
        return exists().where((CollaboratorMapped.User == userId) \
                              & (BlogCollaboratorMapped.blogCollaboratorId == CollaboratorMapped.Id) \
                              & (BlogCollaboratorMapped.Blog == BlogMapped.Id)
                              & (BlogCollaboratorMapped.typeId == BlogCollaboratorTypeMapped.id)
                              & (BlogCollaboratorTypeMapped.Name.in_(self.collaborator_types))) | (BlogMapped.Creator == userId)

# --------------------------------------------------------------------

@setup(IBlogAdminFilterService, name='blogAdminFilterService')
class BlogAdminFilterServiceAlchemy(BlogFilterServiceAlchemyBase, IBlogAdminFilterService):
    '''
    Implementation for @see: IBlogAdminFilterService
    '''
    
    collaborator_type = ['Administrator']
        
@setup(IBlogCollaboratorFilterService, name='blogCollaboratorFilterService')
class BlogCollaboratorFilterServiceAlchemy(BlogFilterServiceAlchemyBase, IBlogCollaboratorFilterService):
    '''
    Implementation for @see: IBlogCollaboratorFilterService
    '''
    
    collaborator_type = ['Administrator', 'Collaborator']
