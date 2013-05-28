'''
Created on May 27, 2013

@package: livedesk
@copyright: 2013 Sourcefabric o.p.s.
@license: http://www.gnu.org/licenses/gpl-3.0.txt
@author: Martin Saturka

Contains the SQL alchemy implementation for comment inlet API.
'''

from ..api.comment import IBlogCommentService
from ..api.blog_post import IBlogPostService, QBlogPost
from ..meta.blog import BlogConfigurationMapped
from ..meta.blog_post import BlogPostMapped
from ally.api.extension import IterPart
from ally.container.ioc import injected
from ally.container.support import setup
from ally.support.sqlalchemy.util_service import buildQuery, buildLimits
from sql_alchemy.impl.entity import EntityServiceAlchemy
from sqlalchemy.orm.exc import NoResultFound
from superdesk.post.api.post import Post
from superdesk.collaborator.api.collaborator import ICollaboratorService, Collaborator
from superdesk.collaborator.meta.collaborator import CollaboratorMapped
from superdesk.user.api.user import IUserService, User
from superdesk.user.meta.user import UserMapped
from superdesk.user.meta.user_type import UserTypeMapped
from superdesk.person.meta.person import PersonMapped
from superdesk.source.api.source import ISourceService, Source
from superdesk.source.meta.source import SourceMapped
from superdesk.source.meta.type import SourceTypeMapped
from datetime import datetime
from ally.container import wire
from ally.exception import InputError, Ref
from ally.internationalization import _
import os, binascii

# --------------------------------------------------------------------

@injected
@setup(IBlogCommentService, name='blogCommentService')
class BlogCommentServiceAlchemy(EntityServiceAlchemy, IBlogCommentService):
    '''
    Implementation for @see: IBlogCommentService
    '''
    blog_comment_config_name = 'Comments'; wire.config('blog_comment_config_name', doc='''
    Name of the blog-specific comments permission configuration''')
    comment_source_type_key = 'comment'; wire.config('comment_source_type_key', doc='''
    Type of the sources for blog comments''')
    comment_source_name_default = 'embed'; wire.config('comment_source_name_default', doc='''
    Default name of the sources for blog comments''')
    comment_post_type_key = 'normal'; wire.config('comment_post_type_key', doc='''
    Type of the posts created on the comment that come via blog comments''')
    comment_user_last_name = 'commentator'; wire.config('comment_user_last_name', doc='''
    The name that is used as LastName for the anonymous users of blog comment posts''')
    comment_user_type_key = 'commentator'; wire.config('comment_user_type_key', doc='''
    The user type that is used for the anonymous users of blog comment posts''')

    blogPostService = IBlogPostService; wire.entity('blogPostService')
    sourceService = ISourceService; wire.entity('sourceService')
    collaboratorService = ICollaboratorService; wire.entity('collaboratorService')
    userService = IUserService; wire.entity('userService')

    def __init__(self):
        '''
        Construct the blog comment service.
        '''
        assert isinstance(self.blogPostService, IBlogPostService), 'Invalid blog post service %s' % self.blogPostService
        assert isinstance(self.sourceService, ISourceService), 'Invalid source service %s' % self.sourceService
        assert isinstance(self.collaboratorService, ICollaboratorService), 'Invalid collaborator service %s' % self.collaboratorService
        assert isinstance(self.userService, IUserService), 'Invalid user service %s' % self.userService

    def getComments(self, blogId, offset=None, limit=None, detailed=False, q=None):
        sql = self.session().query(BlogPostMapped).filter(BlogPostMapped.Blog == blogId)
        sql = sql.join(CollaboratorMapped).join(SourceMapped).join(SourceTypeMapped)
        sql = sql.filter(SourceTypeMapped.Key == self.comment_source_type_key)
        if q:
            assert isinstance(q, QBlogPost), 'Invalid query %s' % q
            sql = buildQuery(sql, q, BlogPostMapped)

        sqlLimit = buildLimits(sql, offset, limit)
        if detailed: return IterPart(sqlLimit.all(), sql.count(), offset, limit)
        return sqlLimit.all()

    def pushMessage(self, blogId, comment):
        '''
        @see: IBlogCommentService.pushMessage
        '''
        # check if the blog (exists and) has comments allowed
        sql = self.session().query(BlogConfigurationMapped.Value)
        sql = sql.filter(BlogConfigurationMapped.parent == blogId)
        sql = sql.filter(BlogConfigurationMapped.Name == self.blog_comment_config_name)
        try:
            allowComments = sql.one()[0]
            if (not allowComments) or allowComments.lower() in ('0', 'f', 'false', 'n', 'no'):
                raise InputError(Ref(_('Comments not allowed for the specified blog'),))
        except:
            raise InputError(Ref(_('Comments not allowed for the specified blog'),))

        userName = comment.UserName
        commentText = comment.CommentText
        commentSource = comment.CommentSource if comment.CommentSource else self.comment_source_name_default

        # checking the necessary info: user name and comment text
        if (userName is None) or (userName == ''):
            raise InputError(Ref(_('No value for the mandatory UserName'),))
        if (commentText is None) or (commentText == ''):
            raise InputError(Ref(_('No value for the mandatory CommentText'),))

        # take (or make) the user (for user name) part of creator and collaborator
        userTypeId, = self.session().query(UserTypeMapped.id).filter(UserTypeMapped.Key == self.comment_user_type_key).one()
        try:
            sql = self.session().query(UserMapped.userId, UserMapped.DeletedOn)
            sql = sql.filter(UserMapped.typeId == userTypeId)
            sql = sql.filter(UserMapped.FirstName == userName)
            userId, isDeleted = sql.one()
            if isDeleted is not None:
                raise InputError(Ref(_('The commentator user was disabled'),))
        except:
            user = User()
            user.FirstName = userName
            user.LastName = self.comment_user_last_name
            user.Name = self._freeCommentUserName()
            user.Password = binascii.b2a_hex(os.urandom(32)).decode()
            user.Type = self.comment_user_type_key
            userId = self.userService.insert(user)

        # make the source (for inlet type) part of collaborator
        try:
            sql = self.session().query(SourceMapped.Id).join(SourceTypeMapped)
            sql = sql.filter(SourceTypeMapped.Key == self.comment_source_type_key).filter(SourceMapped.Name == commentSource)
            sourceId, = sql.one()
        except NoResultFound:
            source = Source()
            source.Type = self.comment_source_type_key
            source.Name = commentSource
            source.URI = ''
            source.IsModifiable = True
            sourceId = self.sourceService.insert(source)

        # make the collaborator
        sql = self.session().query(CollaboratorMapped.Id)
        sql = sql.filter(CollaboratorMapped.Source == sourceId)
        sql = sql.filter(CollaboratorMapped.User == userId)
        try:
            collabId, = sql.one()
        except NoResultFound:
            collab = Collaborator()
            collab.Source = sourceId
            collab.User = userId
            collabId = self.collaboratorService.insert(collab)

        # create post request
        post = Post()
        post.Type = self.comment_post_type_key
        post.Creator = userId
        post.Author = collabId
        post.Content = commentText
        post.CreatedOn = datetime.now()

        # insert the blog post
        postId = self.blogPostService.insert(blogId, post)

        return postId
        #return (self.blogPostService.getById(blogId, postId),)

    # ------------------------------------------------------------------
    def _freeCommentUserName(self):
        userName = 'Comment-' + binascii.b2a_hex(os.urandom(8)).decode()
        while True:
            try:
                userDb = self.session().query(UserMapped).filter(UserMapped.Name == userName).one()
            except:
                return userName

