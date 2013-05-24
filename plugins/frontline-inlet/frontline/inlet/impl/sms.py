'''
Created on April 24, 2013

@package: frontline inlet
@copyright: 2013 Sourcefabric o.p.s.
@license: http://www.gnu.org/licenses/gpl-3.0.txt
@author: Martin Saturka

Contains the SQL alchemy implementation for frontline inlet sms API.
'''

from ..api.sms import ISMSService
from ally.container.ioc import injected
from ally.container.support import setup
from sql_alchemy.impl.entity import EntityServiceAlchemy
from sqlalchemy.orm.exc import NoResultFound
from superdesk.post.api.post import IPostService, Post
from superdesk.collaborator.api.collaborator import ICollaboratorService, Collaborator
from superdesk.collaborator.meta.collaborator import CollaboratorMapped
from superdesk.user.api.user import IUserService, User
from superdesk.user.meta.user import UserMapped
from superdesk.person.meta.person import PersonMapped
from superdesk.source.api.source import ISourceService, Source
from superdesk.source.meta.source import SourceMapped
from superdesk.source.meta.type import SourceTypeMapped
from datetime import datetime
from ally.container import wire
from ally.exception import InputError, Ref
from ally.internationalization import _
import os, binascii

SMS_SOURCE_TYPE_KEY = 'FrontlineSMS'
SMS_POST_TYPE_KEY = 'normal'

# --------------------------------------------------------------------

@injected
@setup(ISMSService, name='smsService')
class SMSServiceAlchemy(EntityServiceAlchemy, ISMSService):
    '''
    Implementation for @see: ISMSService
    '''

    postService = IPostService; wire.entity('postService')
    sourceService = ISourceService; wire.entity('sourceService')
    collaboratorService = ICollaboratorService; wire.entity('collaboratorService')
    userService = IUserService; wire.entity('userService')

    def __init__(self):
        '''
        Construct the frontline sms service.
        '''
        assert isinstance(self.postService, IPostService), 'Invalid post service %s' % self.postService
        assert isinstance(self.sourceService, ISourceService), 'Invalid source service %s' % self.sourceService
        assert isinstance(self.collaboratorService, ICollaboratorService), 'Invalid collaborator service %s' % self.collaboratorService
        assert isinstance(self.userService, IUserService), 'Invalid user service %s' % self.userService

    def pushMessage(self, typeKey, phoneNumber=None, messageText=None, timeStamp=None):
        '''
        @see: ISMSService.pushMessage
        '''
        # checking the necessary info: phone number and message text
        if (phoneNumber is None) or (phoneNumber == ''):
            raise InputError(Ref(_('No value for the mandatory phoneNumber parameter'),))
        if (messageText is None) or (messageText == ''):
            raise InputError(Ref(_('No value for the mandatory messageText parameter'),))

        # take (or make) the user (for phone number) part of creator and collaborator
        try:
            personDb = self.session().query(PersonMapped).filter(PersonMapped.PhoneNumber == phoneNumber).one()
            userId = personDb.Id
        except:
            user = User()
            user.PhoneNumber = phoneNumber
            user.Name = self._freeSMSUserName()
            user.Password = binascii.b2a_hex(os.urandom(32)).decode()
            userId = self.userService.insert(user)

        # make the source (for inlet type) part of collaborator
        try:
            sql = self.session().query(SourceMapped).join(SourceTypeMapped)
            sql = sql.filter(SourceTypeMapped.Key == SMS_SOURCE_TYPE_KEY).filter(SourceMapped.Name == typeKey)
            sourceDb = sql.one()
            sourceId = sourceDb.Id
        except NoResultFound:
            source = Source()
            source.Type = SMS_SOURCE_TYPE_KEY
            source.Name = typeKey
            source.URI = ''
            source.IsModifiable = True
            sourceId = self.sourceService.insert(source)

        # make the collaborator
        sql = self.session().query(CollaboratorMapped)
        sql = sql.filter(CollaboratorMapped.Source == sourceId)
        sql = sql.filter(CollaboratorMapped.User == userId)
        try:
            collabDb = sql.one()
            collabId = collabDb.Id
        except NoResultFound:
            collab = Collaborator()
            collab.Source = sourceId
            collab.User = userId
            collabId = self.collaboratorService.insert(collab)

        # take / make time stamp
        if timeStamp:
            try:
                timeStamp = datetime.strptime(timeStamp, '%Y-%m-%d %H:%M:%S.%f')
            except:
                timeStamp = None

        if not timeStamp:
            timeStamp = datetime.now()

        # create post request
        post = Post()
        post.Type = SMS_POST_TYPE_KEY
        post.Creator = userId
        post.Author = collabId
        post.Content = messageText
        post.CreatedOn = timeStamp

        # insert the post
        postId = self.postService.insert(post)

        return (self.postService.getById(postId),)

    # ------------------------------------------------------------------

    def _freeSMSUserName(self):
        userName = 'SMS-' + binascii.b2a_hex(os.urandom(8)).decode()
        while True:
            try:
                userDb = self.session().query(UserMapped).filter(UserMapped.Name == userName).one()
            except:
                return userName

