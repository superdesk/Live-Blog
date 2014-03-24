'''
Created on May 4, 2012

@package: livedesk
@copyright: 2012 Sourcefabric o.p.s.
@license: http://www.gnu.org/licenses/gpl-3.0.txt
@author: Gabriel Nistor

Contains the SQL alchemy meta for blog collaborator API.
'''

from sqlalchemy.exc import OperationalError
from sqlalchemy.orm.exc import NoResultFound
from sqlalchemy.sql.expression import not_

from ally.api.error import InputError
from ally.api.validate import validate
from ally.container import wire
from ally.container.ioc import injected
from ally.container.support import setup
from ally.internationalization import _
from ally.support.api.util_service import processCollection
from livedesk.api.blog_collaborator import BlogCollaborator
from livedesk.api.blog_collaborator_type import \
    IBlogCollaboratorTypeActionService
from livedesk.meta.blog import BlogMapped
from livedesk.meta.blog_collaborator import BlogCollaboratorMapped, \
    BlogCollaboratorEntry, BlogCollaboratorTypeMapped
from sql_alchemy.support.util_service import SessionSupport, iterateCollection, \
    buildQuery
from superdesk.collaborator.meta.collaborator import CollaboratorMapped
from superdesk.security.api.user_rbac import IUserRbacService
from superdesk.source.meta.source import SourceMapped
from superdesk.user.meta.user import UserMapped

from ..api.blog_collaborator import IBlogCollaboratorService


# --------------------------------------------------------------------
@injected
@setup(IBlogCollaboratorService, name='blogCollaboratorService')
@validate(BlogCollaboratorMapped)
class BlogCollaboratorServiceAlchemy(SessionSupport, IBlogCollaboratorService):
    '''
    Implementation for @see: IBlogCollaboratorService
    '''

    userRbacService = IUserRbacService; wire.entity('userRbacService')
    blogCollaboratorTypeActionService = IBlogCollaboratorTypeActionService; wire.entity('blogCollaboratorTypeActionService')

    def __init__(self):
        '''
        Construct the blog collaborator service.
        '''
        assert isinstance(self.userRbacService, IUserRbacService), \
        'Invalid user actions service %s' % self.userRbacService
        assert isinstance(self.blogCollaboratorTypeActionService, IBlogCollaboratorTypeActionService), \
        'Invalid collaborator actions service %s' % self.blogCollaboratorTypeActionService
        super().__init__()

    def getById(self, blogId, collaboratorId):
        '''
        @see: IBlogCollaboratorService.getById
        '''
        sql = self.session().query(BlogCollaboratorMapped)
        sql = sql.filter(BlogCollaboratorMapped.Blog == blogId)
        sql = sql.filter(BlogCollaboratorMapped.Id == collaboratorId)

        try: return sql.one()
        except NoResultFound: raise InputError(_('No collaborator'), BlogCollaboratorMapped.Id)
        
    def getActions(self, userId, blogId, **options):
        '''
        @see: IBlogCollaboratorService.getActions
        '''
        actions = set(self.userRbacService.getActions(userId))
        typeName = self.collaboratorType(userId, blogId)
        if typeName: actions.update(set(self.blogCollaboratorTypeActionService.getActions(typeName)))
        
        return processCollection(actions, **options)
        
    def getActionsRoot(self, userId, blogId, **options):
        '''
        @see: IBlogCollaboratorService.getActionsRoot
        '''
        actions = set(self.userRbacService.getActionsRoot(userId))
        typeName = self.collaboratorType(userId, blogId)
        if typeName:
            actions.update(set(self.blogCollaboratorTypeActionService.getActionsRoot(typeName)))
        
        return processCollection(actions, **options)
        
    def getSubActions(self, userId, blogId, parentPath, **options):
        '''
        @see: IBlogCollaboratorService.getSubActions
        '''
        actions = set(self.userRbacService.getSubActions(userId, parentPath))
        typeName = self.collaboratorType(userId, blogId)
        if typeName: actions.update(set(self.blogCollaboratorTypeActionService.getSubActions(typeName, parentPath)))
        
        return processCollection(actions, **options)

    def getAll(self, blogId, **options):
        '''
        @see: IBlogCollaboratorService.getAll
        '''
        sql = self.session().query(BlogCollaboratorMapped.Id).filter(BlogCollaboratorMapped.Blog == blogId)
        sql = sql.join(UserMapped).join(SourceMapped).order_by(BlogCollaboratorMapped.Name)
        sql = sql.filter(UserMapped.Active == True)
        return iterateCollection(sql, **options)

    def getPotential(self, blogId, excludeSources=True, qu=None, qs=None, **options):
        '''
        @see: IBlogCollaboratorService.getPotential
        '''
        sqlBlog = self.session().query(BlogCollaboratorMapped.Id).filter(BlogCollaboratorMapped.Blog == blogId)
        sql = self.session().query(CollaboratorMapped).join(UserMapped).join(SourceMapped)
        sql = sql.filter(not_(CollaboratorMapped.Id.in_(sqlBlog)))
        sql = sql.filter(UserMapped.Active == True)
        sql = sql.order_by(CollaboratorMapped.Name)
        if excludeSources: sql = sql.filter(CollaboratorMapped.User != None)
        if qu: sql = buildQuery(sql, qu, UserMapped)
        if qs: sql = buildQuery(sql, qs, SourceMapped)
        return iterateCollection(sql, **options)

    def addCollaboratorAsDefault(self, blogId, collaboratorId):
        '''
        @see: IBlogCollaboratorService.addCollaboratorAsDefault
        '''
        sql = self.session().query(BlogCollaboratorTypeMapped.Name)
        sql = sql.filter(BlogCollaboratorTypeMapped.IsDefault == True)
        
        try: typeName, = sql.one()
        except NoResultFound: raise InputError(_('No default collaborator type is available'))
        
        self.addCollaborator(blogId, collaboratorId, typeName)

    def addCollaborator(self, blogId, collaboratorId, typeName):
        '''
        @see: IBlogCollaboratorService.addCollaborator
        '''
        typeId = self.typeId(typeName)
        if typeId is None: raise InputError(_('Invalid collaborator type'), BlogCollaborator.Type)

        sql = self.session().query(BlogCollaboratorEntry)
        sql = sql.filter(BlogCollaboratorEntry.Blog == blogId)
        sql = sql.filter(BlogCollaboratorEntry.blogCollaboratorId == collaboratorId)
        if sql.update({BlogCollaboratorEntry.typeId: typeId}) > 0: return

        sql = self.session().query(BlogCollaboratorMapped.Id)
        sql = sql.join(BlogMapped)
        sql = sql.filter(BlogCollaboratorMapped.User == BlogMapped.Creator)
        sql = sql.filter(BlogMapped.Id == blogId)
        sql = sql.filter(BlogCollaboratorMapped.Id == collaboratorId)
        if sql.count() > 0: raise InputError(_('The blog creator cannot be assigned as a collaborator'))

        bgc = BlogCollaboratorEntry()
        bgc.Blog = blogId
        bgc.blogCollaboratorId = collaboratorId
        bgc.typeId = typeId
        self.session().add(bgc)
        self.session().flush((bgc,))

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
            raise InputError(_('Cannot remove'), BlogCollaboratorMapped)

    # ----------------------------------------------------------------
    
    def collaboratorType(self, userId, blogId):
        ''' Provides the collaborator type name, if one is available.'''
        sql = self.session().query(BlogCollaboratorTypeMapped.Name).join(BlogCollaboratorMapped)
        sql = sql.filter(BlogCollaboratorMapped.User == userId).filter(BlogCollaboratorMapped.Blog == blogId)
        
        try: typeName, = sql.one()
        except NoResultFound: return
        return typeName
    
    def typeId(self, typeName):
        ''' Provides the collaborator type name, if one is available.'''
        sql = self.session().query(BlogCollaboratorTypeMapped.id)
        sql = sql.filter(BlogCollaboratorTypeMapped.Name == typeName)
        
        try: typeId, = sql.one()
        except NoResultFound: return
        return typeId
