'''
Created on May 4, 2012

@package: livedesk
@copyright: 2012 Sourcefabric o.p.s.
@license: http://www.gnu.org/licenses/gpl-3.0.txt
@author: Gabriel Nistor

Contains the SQL alchemy meta for blog collaborator API.
'''

from ..api.blog_collaborator import IBlogCollaboratorService
from acl.api.filter import IAclFilter
from acl.spec import Filter
from ally.api.extension import IterPart
from ally.container import wire
from ally.container.ioc import injected
from ally.container.support import setup
from ally.exception import InputError, Ref
from ally.internationalization import _
from ally.support.sqlalchemy.session import SessionSupport
from ally.support.sqlalchemy.util_service import buildQuery, buildLimits
from livedesk.api.blog_collaborator import BlogCollaborator
from livedesk.meta.blog import BlogMapped
from livedesk.meta.blog_collaborator import BlogCollaboratorMapped, \
    BlogCollaboratorEntry, BlogCollaboratorTypeMapped
from sqlalchemy.exc import OperationalError
from sqlalchemy.orm.exc import NoResultFound
from sqlalchemy.sql.expression import not_
from superdesk.collaborator.meta.collaborator import CollaboratorMapped
from superdesk.security.api.user_action import IUserActionService
from superdesk.source.meta.source import SourceMapped
from superdesk.user.meta.user import UserMapped

# --------------------------------------------------------------------

@injected
class CollaboratorSpecification:
    '''
    The class that provides the collaborator configurations.
    '''

    collaborator_types = list
    # The collaborator types to be assigned to added blog collaborators, if the type is not specified then the first entry
    # is used.
    type_filter = list  # list[tuple(string, Filter)]
    # Contains the user to blog filter to be used for a certain type, this have to be in the proper order.
    type_actions = dict
    # The action names to be associated with a collaborator type.

    def __init__(self):
        assert isinstance(self.collaborator_types, list), 'Invalid collaborator types %s' % self.collaborator_types
        assert isinstance(self.type_filter, list), 'Invalid type filter %s' % self.type_filter
        assert isinstance(self.type_actions, dict), 'Invalid type actions %s' % self.type_actions
        if __debug__:
            for name in self.collaborator_types: assert isinstance(name, str), 'Invalid collaborator type name %s' % name

@injected
@setup(IBlogCollaboratorService, name='blogCollaboratorService')
class BlogCollaboratorServiceAlchemy(SessionSupport, IBlogCollaboratorService):
    '''
    Implementation for @see: IBlogCollaboratorService
    '''

    collaboratorSpecification = CollaboratorSpecification; wire.entity('collaboratorSpecification')
    userActionService = IUserActionService; wire.entity('userActionService')

    def __init__(self):
        '''
        Construct the blog collaborator service.
        '''
        assert isinstance(self.collaboratorSpecification, CollaboratorSpecification), \
        'Invalid collaborator specification %s' % self.collaboratorSpecification
        assert isinstance(self.userActionService, IUserActionService), \
        'Invalid user actions service %s' % self.userActionService
        super().__init__()

        self._collaboratorTypeIds = {}

    def getAllTypes(self):
        '''
        @see: IBlogCollaboratorService.getAllTypes
        '''
        return self.session().query(BlogCollaboratorTypeMapped).all()

    def getActions(self, userId, blogId, path=None, origPath=None):
        '''
        @see: IBlogCollaboratorService.getActions
        '''
        actions = list(self.userActionService.getAll(userId, path))
        paths = { a.Path for a in actions }
        for name, f in self.collaboratorSpecification.type_filter:
            assert isinstance(f, Filter), 'Invalid filter'
            assert isinstance(f.filter, IAclFilter)
            if f.filter.isAllowed(userId, blogId):
                collActions = list(self.collaboratorSpecification.type_actions.get(name))
                collPaths = { a.Path for a in collActions }.difference(paths)
                actions.extend([action for action in collActions if action.Path in collPaths])
                break
        return actions

    def getById(self, blogId, collaboratorId):
        '''
        @see: IBlogCollaboratorService.getById
        '''
        sql = self.session().query(BlogCollaboratorMapped)
        sql = sql.filter(BlogCollaboratorMapped.Blog == blogId)
        sql = sql.filter(BlogCollaboratorMapped.Id == collaboratorId)

        try: return sql.one()
        except NoResultFound: raise InputError(Ref(_('No collaborator'), ref=BlogCollaboratorMapped.Id))

    def getAll(self, blogId, offset=None, limit=None, detailed=True):
        '''
        @see: IBlogCollaboratorService.getAll
        '''
        sql = self.session().query(BlogCollaboratorMapped).filter(BlogCollaboratorMapped.Blog == blogId)
        sql = sql.join(UserMapped).join(SourceMapped).order_by(BlogCollaboratorMapped.Name)
        sql = sql.filter(UserMapped.Active == True)
        sqlLimit = buildLimits(sql, offset, limit)
        if detailed: return IterPart(sqlLimit.all(), sql.count(), offset, limit)
        return sqlLimit.all()

    def getPotential(self, blogId, excludeSources=True, offset=None, limit=None, detailed=True, qu=None, qs=None):
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
        sqlLimit = buildLimits(sql, offset, limit)
        if detailed: return IterPart(sqlLimit.all(), sql.count(), offset, limit)
        return sqlLimit.all()

    def addCollaboratorAsDefault(self, blogId, collaboratorId):
        '''
        @see: IBlogCollaboratorService.addCollaboratorAsDefault
        '''
        self.addCollaborator(blogId, collaboratorId, self.collaboratorSpecification.collaborator_types[0])

    def addCollaborator(self, blogId, collaboratorId, typeName):
        '''
        @see: IBlogCollaboratorService.addCollaborator
        '''
        typeId = self.collaboratorTypeIds()[typeName]
        if typeId is None: raise InputError(Ref(_('Invalid collaborator type'), ref=BlogCollaborator.Type))

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
            raise InputError(Ref(_('Cannot remove'), model=BlogCollaboratorMapped))

    # ----------------------------------------------------------------

    def collaboratorTypeIds(self):
        '''
        Provides the collaborator types ids dictionary.
        '''
        if not self._collaboratorTypeIds:
            for name in self.collaboratorSpecification.collaborator_types:
                sql = self.session().query(BlogCollaboratorTypeMapped)
                sql = sql.filter(BlogCollaboratorTypeMapped.Name == name)
                try: bt = sql.one()
                except NoResultFound:
                    bt = BlogCollaboratorTypeMapped()
                    bt.Name = name
                    self.session().add(bt)
                    self.session().flush((bt,))
                self._collaboratorTypeIds[name] = bt.id
        return self._collaboratorTypeIds
