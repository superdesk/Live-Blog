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

# --------------------------------------------------------------------

class BlogFilterServiceAlchemyBase(SessionSupport):
    '''
    Generic implementation for blog filter service.
    '''
    
    collaborator_types = list
    
    def __init__(self):
        assert isinstance(self.collaborator_types, list), 'Invalid collaborator types %s' % self.collaborator_types
        super().__init__()
    
    def isAllowed(self, userId, blogId):
        '''
        @see: IBlogAdminFilterService.isAllowed
        '''
        sql = self.session().query(BlogMapped.Id)
        sql = sql.filter(BlogMapped.Id == blogId)
        sql = sql.filter(BlogMapped.Creator == userId)
        if sql.count() > 0: return True
        
        sql = self.session().query(BlogCollaboratorMapped.Id)
        sql = sql.join(BlogCollaboratorTypeMapped)
        sql = sql.filter(BlogCollaboratorMapped.Blog == blogId)
        sql = sql.filter((BlogCollaboratorMapped.User == userId) & BlogCollaboratorTypeMapped.Name.in_(self.collaborator_types))
        return sql.count() > 0

# --------------------------------------------------------------------

@setup(IBlogAdminFilterService, name='blogAdminFilterService')
class BlogAdminFilterServiceAlchemy(BlogFilterServiceAlchemyBase, IBlogAdminFilterService):
    '''
    Implementation for @see: IBlogAdminFilterService
    '''
    
    collaborator_types = ['Administrator']; wire.config('collaborator_types', doc='''
    The collaborator type(s) name associated with the administrator filter.
    ''')
    
    def __init__(self): super().__init__()
        
@setup(IBlogCollaboratorFilterService, name='blogCollaboratorFilterService')
class BlogCollaboratorFilterServiceAlchemy(BlogFilterServiceAlchemyBase, IBlogCollaboratorFilterService):
    '''
    Implementation for @see: IBlogCollaboratorFilterService
    '''
    
    collaborator_types = ['Administrator', 'Collaborator']; wire.config('collaborator_types', doc='''
    The collaborator type(s) name associated with the collaborator filter.
    ''')
    
    def __init__(self): super().__init__()
