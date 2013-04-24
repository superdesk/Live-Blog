'''
Created on April 24, 2013

@package: feed sms
@copyright: 2013 Sourcefabric o.p.s.
@license: http://www.gnu.org/licenses/gpl-3.0.txt
@author: Martin Saturka

API specifications for sms feed.
'''

from ally.api.config import service, call, query, LIMIT_DEFAULT, GET
from ally.api.criteria import AsLikeOrdered, AsDateTimeOrdered
from ally.api.type import Iter
from ally.support.api.entity import Entity, IEntityService, QEntity
from ..api.domain_feed import modelFeed
from ..api.sms_feed_type import SMSFeedType

# --------------------------------------------------------------------

@modelFeed
class SMSFeed(Entity):
    '''
    Provides the sms feed model.
    '''
    Type = SMSFeedType
    PhoneNumber = str
    ReceivedOn = datetime
    MessageText = str

# --------------------------------------------------------------------

@query(SMSFeed)
class QSMSFeed(QEntity):
    '''
    Provides the query for sms feed model.
    '''
    phoneNumber = AsLikeOrdered
    receivedOn = AsDateTimeOrdered
    messageText = AsLikeOrdered

# --------------------------------------------------------------------

@service((Entity, SMSFeed))
class ISMSFeedService(IEntityService):
    '''
    Provides the service methods for the sms feeds.
    '''

    @call(method=GET)
    def getAll(self, typeKey:SMSFeedType.Key=None, offset:int=None, limit:int=LIMIT_DEFAULT, detailed:bool=True,
               q:QSMSFeed=None) -> Iter(SMSFeed):
        '''
        Provides all the available sms feeds.
        '''

    @call(method=GET)
    def insertMessage(self, typeKey:SMSFeedType.Key, q:QSMSFeed=None) -> Iter(SMSFeed):
        '''
        Inserts a new message.
        TODO: this is a temporary solution, since we do not support the format of FrontlineSMS POST messages
        '''

