'''
Created on May 4, 2012

@package: livedesk
@copyright: 2012 Sourcefabric o.p.s.
@license: http://www.gnu.org/licenses/gpl-3.0.txt
@author: Gabriel Nistor

Contains the SQL alchemy meta for blog collaborator API.
'''

from ..api.blog_collaborator import IBlogCollaboratorService
from ally.container.ioc import injected
from ally.support.sqlalchemy.util_service import buildLimits
from livedesk.meta.blog_collaborator import BlogCollaboratorMapped
from sql_alchemy.impl.entity import EntityGetServiceAlchemy
from sqlalchemy.exc import OperationalError
from ally.exception import InputError, Ref
from ally.internationalization import _

# --------------------------------------------------------------------

@injected
class BlogCollaboratorServiceAlchemy(EntityGetServiceAlchemy, IBlogCollaboratorService):
    '''
    Implementation for @see: IBlogCollaboratorService
    '''

    def __init__(self):
        '''
        Construct the blog collaborator service.
        '''
        EntityGetServiceAlchemy.__init__(self, BlogCollaboratorMapped)

    def getAll(self, blogId=None, collaboratorId=None, offset=None, limit=None):
        '''
        @see: IBlogCollaboratorService.getAll
        '''
        sql = self.session().query(BlogCollaboratorMapped)
        if blogId: sql = sql.filter(BlogCollaboratorMapped.Blog == blogId)
        if collaboratorId: sql = sql.filter(BlogCollaboratorMapped.Collaborator == collaboratorId)
        sql = buildLimits(sql, offset, limit)
        return sql.all()

    def addCollaborator(self, blogId, collaboratorId):
        '''
        @see: IBlogCollaboratorService.addCollaborator
        '''
        sql = self.session().query(BlogCollaboratorMapped)
        sql = sql.filter(BlogCollaboratorMapped.Blog == blogId)
        sql = sql.filter(BlogCollaboratorMapped.Collaborator == collaboratorId)
        if sql.count() > 0: raise InputError(_('Already a collaborator for this blog'))

        bgc = BlogCollaboratorMapped()
        bgc.Blog = blogId
        bgc.Collaborator = collaboratorId
        self.session().add(bgc)
        self.session().flush((bgc,))
        return bgc.Id

    def removeCollaborator(self, blogId, collaboratorId):
        '''
        @see: IBlogCollaboratorService.removeCollaborator
        '''
        try:
            sql = self.session().query(BlogCollaboratorMapped)
            sql = sql.filter(BlogCollaboratorMapped.Blog == blogId)
            sql = sql.filter(BlogCollaboratorMapped.Collaborator == collaboratorId)
            return sql.delete() > 0
        except OperationalError:
            raise InputError(Ref(_('Cannot remove'), model=BlogCollaboratorMapped))

    def remove(self, blogCollaboratorId):
        '''
        @see: IBlogCollaboratorService.remove
        '''
        try:
            return self.session().query(BlogCollaboratorMapped).filter(BlogCollaboratorMapped.Id == id).delete() > 0
        except OperationalError:
            raise InputError(Ref(_('Cannot remove'), model=BlogCollaboratorMapped))
