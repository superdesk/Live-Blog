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
from superdesk.user.meta.user import UserMapped
from superdesk.source.api.source import ISourceService, Source
from superdesk.source.meta.source import SourceMapped
from superdesk.source.meta.type import SourceTypeMapped
from datetime import datetime
from ally.container import wire

SMS_SYSTEM_PERSON_ID = 1
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

    def __init__(self):
        '''
        Construct the frontline sms service.
        '''
        assert isinstance(self.postService, IPostService), 'Invalid post service %s' % self.postService
        assert isinstance(self.sourceService, ISourceService), 'Invalid source service %s' % self.sourceService
        assert isinstance(self.collaboratorService, ICollaboratorService), 'Invalid collaborator service %s' % self.collaboratorService

    def pushMessage(self, typeKey, phoneNumber, messageText):
        '''
        @see: ISMSService.pushMessage
        '''
        # make the source (for inlet type) part of collaborator
        sql = self.session().query(SourceMapped).join(SourceTypeMapped)
        sql = sql.filter(SourceTypeMapped.Key == SMS_SOURCE_TYPE_KEY).filter(SourceMapped.Name == typeKey)

        try:
            sourceDb = sql.one()
            sourceId = sourceDb.Id
        except NoResultFound:
            source = Source()
            source.Type = SMS_SOURCE_TYPE_KEY
            source.Name = typeKey
            source.URI = ''
            source.IsModifiable = True
            sourceId = self.sourceService.insert(source)

        # take the user (for phone number) part of collaborator
        try:
            userDb = self.session().query(UserMapped).filter(UserMapped.PhoneNumber == phoneNumber).one()
            userId = userDb.Id
        except:
            userId = None

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

        # create post request
        post = Post()
        post.Type = SMS_POST_TYPE_KEY
        post.Creator = SMS_SYSTEM_PERSON_ID
        post.Author = collabId
        post.Content = messageText
        post.CreatedOn = datetime.now()

        # insert the post
        postId = self.postService.insert(post)

        return (self.postService.getById(postId),)

