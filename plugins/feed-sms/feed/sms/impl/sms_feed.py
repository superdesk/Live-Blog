'''
Created on April 24, 2013

@package: feed sms
@copyright: 2013 Sourcefabric o.p.s.
@license: http://www.gnu.org/licenses/gpl-3.0.txt
@author: Martin Saturka

Contains the SQL alchemy implementation for sms feed API.
'''

from ..api.sms_feed import ISMSFeedService, QSMSFeed
from ..meta.sms_feed import SMSFeedMapped
from ..meta.sms_feed_type import SMSFeedTypeMapped
from ally.container.ioc import injected
from ally.container.support import setup
from ally.exception import InputError, Ref
from ally.internationalization import _
from ally.support.sqlalchemy.util_service import buildQuery, buildLimits, handle
from sql_alchemy.impl.entity import EntityServiceAlchemy
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm.exc import NoResultFound
from ally.api.extension import IterPart
from sqlalchemy.sql.functions import current_timestamp
from ally.api.criteria import AsLike
from superdesk.post.api.post import IPostService, Post
from superdesk.collaborator.api.collaborator import Collaborator
from superdesk.post.api.type import PostType
from superdesk.user.api.user import User
from datetime import datetime
from ally.container import wire
from superdesk.user.api.user import IUserService
from livedesk.impl.blog_collaborator import CollaboratorSpecification

# --------------------------------------------------------------------

@injected
@setup(ISMSFeedService, name='smsFeedService')
class SMSFeedServiceAlchemy(EntityServiceAlchemy, ISMSFeedService):
    '''
    Implementation for @see: ISMSFeedService
    '''

    postService = IPostService; wire.entity('postService')
    collaboratorSpecification = CollaboratorSpecification; wire.entity('collaboratorSpecification')
    # the search provider used to search the article list
    userService = IUserService; wire.entity('userService')
    # the user service used to set the creator
    authorService = IUserService; wire.entity('authorService')
    # the author service used to set the author

    def __init__(self):
        '''
        Construct the sms feed service.
        '''
        assert isinstance(self.postService, IPostService), 'Invalid post service %s' % self.postService
        EntityServiceAlchemy.__init__(self, SMSFeedMapped)

    def getAll(self, typeKey=None, offset=None, limit=None, detailed=False, q=None):
        '''
        @see: ISMSFeedService.getAll
        '''
        sql = self.session().query(SMSFeedMapped)
        if typeKey:
            sql = sql.join(SMSFeedTypeMapped).filter(SMSFeedTypeMapped.Key == typeKey)
        if q:
            sql = buildQuery(sql, q, TaskLinkMapped)
        sqlLimit = buildLimits(sql, offset, limit)
        if detailed: return IterPart(sqlLimit.all(), sql.count(), offset, limit)
        return sqlLimit.all()

    def pushMessage(self, typeKey, q=None):
        '''
        @see: ISMSFeedService.pushMessage
        '''
        smsFeedDb = SMSFeedMapped()
        smsFeedDb.typeId = self._feedTypeId(typeKey)

        smsFeedDb.ReceivedOn = current_timestamp()

        if q:
            if (QSMSFeed.phoneNumber in q) and (AsLike.like in q.phoneNumber):
                smsFeedDb.PhoneNumber = q.phoneNumber.like
            if (QSMSFeed.messageText in q) and (AsLike.like in q.messageText):
                smsFeedDb.MessageText = q.messageText.like

        if not smsFeedDb.PhoneNumber:
            raise InputError(Ref(_('Not enough info for a message'),))

        try:
            self.session().add(smsFeedDb)
            self.session().flush((smsFeedDb,))

        except SQLAlchemyError as e:
            handle(e, smsFeedDb)

        post = Post()
        post.Type = PostType('SMS').Key
        post.Creator = User().Id
        post.Author = Collaborator().Id
        post.IsModified = False
        post.IsPublished = False
        post.Meta = smsFeedDb.PhoneNumber
        post.ContentPlain = smsFeedDb.MessageText
        post.Content = smsFeedDb.MessageText
        post.CreatedOn = datetime.now()
        post.PublishedOn = None
        post.UpdatedOn = None
        post.DeletedOn = None
        post.AuthorName = ''
        blogPostId=self.postService.insert(post)

        return (smsFeedDb,)

    # ----------------------------------------------------------------

    def _feedTypeId(self, key):
        '''
        Provides the sms feed type id that has the provided key.
        '''
        try:
            sql = self.session().query(SMSFeedTypeMapped.id).filter(SMSFeedTypeMapped.Key == key)
            return sql.one()[0]
        except NoResultFound:
            raise InputError(Ref(_('Invalid sms feed type %(type)s') % dict(type=key),))
