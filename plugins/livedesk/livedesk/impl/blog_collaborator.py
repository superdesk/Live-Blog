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
from livedesk.meta.blog_collaborator import BlogCollaboratorMapped, \
    BlogCollaboratorEntry
from superdesk.person.meta.person import PersonMapped
from superdesk.source.meta.source import SourceMapped
from sqlalchemy.exc import OperationalError
from ally.exception import InputError, Ref
from ally.internationalization import _
from ally.support.sqlalchemy.session import SessionSupport
from ally.container.support import setup
from sqlalchemy.orm.exc import NoResultFound

# --------------------------------------------------------------------

@injected
@setup(IBlogCollaboratorService)
class BlogCollaboratorServiceAlchemy(SessionSupport, IBlogCollaboratorService):
    '''
    Implementation for @see: IBlogCollaboratorService
    '''

    def __init__(self):
        '''
        Construct the blog collaborator service.
        '''

    def getById(self, blogId, collaboratorId):
        '''
        @see: IBlogCollaboratorService.getById
        '''
        sql = self.session().query(BlogCollaboratorMapped)
        sql = sql.filter(BlogCollaboratorMapped.Blog == blogId)
        sql = sql.filter(BlogCollaboratorMapped.Id == collaboratorId)

        try: return sql.one()
        except NoResultFound: raise InputError(Ref(_('No collaborator'), ref=BlogCollaboratorMapped.Id))

    def getAll(self, blogId):
        '''
        @see: IBlogCollaboratorService.getAll
        '''
        sql = self.session().query(BlogCollaboratorMapped).filter(BlogCollaboratorMapped.Blog == blogId)
        sql = sql.join(PersonMapped).join(SourceMapped).order_by(BlogCollaboratorMapped.Name)
        return sql.all()

    def addCollaborator(self, blogId, collaboratorId):
        '''
        @see: IBlogCollaboratorService.addCollaborator
        '''
        sql = self.session().query(BlogCollaboratorEntry)
        sql = sql.filter(BlogCollaboratorEntry.Blog == blogId)
        sql = sql.filter(BlogCollaboratorEntry.blogCollaboratorId == collaboratorId)
        if sql.count() > 0: raise InputError(_('Already a collaborator for this blog'))

        bgc = BlogCollaboratorEntry()
        bgc.Blog = blogId
        bgc.blogCollaboratorId = collaboratorId
        self.session().add(bgc)
        self.session().flush((bgc,))
        return bgc.blogCollaboratorId

    def removeCollaborator(self, blogId, collaboratorId):
        '''
        @see: IBlogCollaboratorService.removeCollaborator
        '''
        try:
            sql = self.session().query(BlogCollaboratorEntry)
            sql = sql.filter(BlogCollaboratorEntry.Blog == blogId)
            sql = sql.filter(BlogCollaboratorEntry.blogCollaboratorId == collaboratorId)
            return sql.delete() > 0
        except OperationalError:
            raise InputError(Ref(_('Cannot remove'), model=BlogCollaboratorMapped))
