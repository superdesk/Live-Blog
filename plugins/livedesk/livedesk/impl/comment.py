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
from ..meta.blog import BlogMapped
from ..meta.blog_post import BlogPostMapped
from ally.container.ioc import injected
from ally.container.support import setup
from sql_alchemy.impl.entity import EntityServiceAlchemy
from sqlalchemy.orm.exc import NoResultFound
from sqlalchemy.sql.expression import exists
from superdesk.post.api.post import Post
from superdesk.collaborator.api.collaborator import ICollaboratorService, Collaborator
from superdesk.collaborator.meta.collaborator import CollaboratorMapped
from superdesk.user.api.user import IUserService, User
from superdesk.user.meta.user import UserMapped
from superdesk.user.meta.user_type import UserTypeMapped
from superdesk.source.api.source import ISourceService, Source
from superdesk.source.meta.source import SourceMapped
from superdesk.source.meta.type import SourceTypeMapped
from datetime import datetime
from ally.container import wire
from ally.internationalization import _
import os, binascii
from sql_alchemy.support.util_service import buildQuery, iterateCollection
from ally.api.error import InputError
from ally.api.validate import validate, Mandatory
from livedesk.api.comment import BlogComment

# --------------------------------------------------------------------

@injected
@setup(IBlogCommentService, name='blogCommentService')
@validate(Mandatory(BlogComment.UserName), Mandatory(BlogComment.Text), Mandatory(BlogComment.Source))
class BlogCommentServiceAlchemy(EntityServiceAlchemy, IBlogCommentService):
    '''
    Implementation for @see: IBlogCommentService
    '''
    blog_config_name = 'Comments'; wire.config('blog_config_name', doc='''
    Name of the blog-specific comments permission configuration''')
    source_type_key = 'comment'; wire.config('source_type_key', doc='''
    Type of the sources for blog comments''')
    source_name_default = 'embed'; wire.config('source_name_default', doc='''
    Default name of the sources for blog comments''')
    post_type_key = 'normal'; wire.config('post_type_key', doc='''
    Type of the posts created on the comment that come via blog comments''')
    user_last_name = 'commentator'; wire.config('user_last_name', doc='''
    The name that is used as LastName for the anonymous users of blog comment posts''')
    user_type_key = 'commentator'; wire.config('user_type_key', doc='''
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

    def getComments(self, blogId, q=None, **options):
        '''
        @see: IBlogCommentService.getComments
        '''
        sql = self.session().query(BlogPostMapped).filter(BlogPostMapped.Blog == blogId)
        sql = sql.join(CollaboratorMapped).join(SourceMapped).join(SourceTypeMapped)
        sql = sql.filter(SourceTypeMapped.Key == self.source_type_key)
        if q:
            assert isinstance(q, QBlogPost), 'Invalid query %s' % q
            sql = buildQuery(sql, q, BlogPostMapped)

        return iterateCollection(sql, **options)

    def getOriginalComments(self, blogId, q=None, **options):
        '''
        @see: IBlogCommentService.getOriginalComments
        TODO: this is just for enabling the comment-post URL in the resources
        '''
        return ()

    def addComment(self, blogId, comment):
        '''
        @see: IBlogCommentService.addComment
        '''
        # checking if the blog exists
        # checking whether comments are allowed shall be done in gateway
        if not self.session().query(exists().where(BlogMapped.Id == blogId)).scalar():
            raise InputError(_('Specified blog does not exist'),)

        userName = comment.UserName
        commentText = comment.Text
        commentSource = comment.Source if comment.Source else self.source_name_default

        # checking the necessary info: user name and comment text
        if not userName:
            raise InputError(_('No value for the mandatory UserName'),)
        if not commentText:
            raise InputError(_('No value for the mandatory Text field'),)

        # take (or make) the user (for user name) part of creator and collaborator
        userTypeId, = self.session().query(UserTypeMapped.id).filter(UserTypeMapped.Key == self.user_type_key).one()
        try:
            sql = self.session().query(UserMapped.userId, UserMapped.Active)
            sql = sql.filter(UserMapped.Type == userTypeId)
            sql = sql.filter(UserMapped.FirstName == userName)
            userId, isActive = sql.one()
            if not isActive:
                raise InputError(_('The commentator user was inactivated'),)
        except:
            user = User()
            user.FirstName = userName
            user.LastName = self.user_last_name
            user.Name = self._freeCommentUserName()
            user.Password = binascii.b2a_hex(os.urandom(32)).decode()
            user.Type = self.user_type_key
            userId = self.userService.insert(user)

        # make the source (for inlet type) part of collaborator
        try:
            sql = self.session().query(SourceMapped.Id).join(SourceTypeMapped)
            sql = sql.filter(SourceTypeMapped.Key == self.source_type_key).filter(SourceMapped.Name == commentSource)
            sourceId, = sql.one()
        except NoResultFound:
            source = Source()
            source.Type = self.source_type_key
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
        post.Type = self.post_type_key
        post.Creator = userId
        post.Author = collabId
        post.Content = commentText
        post.CreatedOn = datetime.now()

        # insert the blog post
        postId = self.blogPostService.insert(blogId, post)

        return postId

    # ------------------------------------------------------------------
    def _freeCommentUserName(self):
        userName = 'Comment-' + binascii.b2a_hex(os.urandom(8)).decode()
        while True:
            try:
                _userDb = self.session().query(UserMapped).filter(UserMapped.Name == userName).one()
            except:
                return userName

