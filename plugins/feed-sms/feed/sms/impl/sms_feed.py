'''
Created on April 24, 2013

@package: feed sms
@copyright: 2013 Sourcefabric o.p.s.
@license: http://www.gnu.org/licenses/gpl-3.0.txt
@author: Martin Saturka

Contains the SQL alchemy implementation for sms feed API.
'''

from ..api.sms_feed import ISMSFeedService, SMSFeed
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

# --------------------------------------------------------------------

@injected
@setup(ISMSFeedService, name='smsFeedService')
class SMSFeedServiceAlchemy(EntityServiceAlchemy, ISMSFeedService):
    '''
    Implementation for @see: ISMSFeedService
    '''

    def __init__(self):
        '''
        Construct the sms feed service.
        '''
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

    def insertMessage(self, typeKey, q=None):
        '''
        @see: ISMSFeedService.insertMessage
        '''
        smsFeedDb = SMSFeedMapped()
        smsFeedDb.typeId = self._feedTypeId(typeKey)

        smsFeedDb.ReceivedOn = current_timestamp()

        if q:
            if SMSFeed.phoneNumber in q and q.phoneNumber:
                smsFeedDb.PhoneNumber = q.phoneNumber
            if SMSFeed.messageText in q and q.messageText:
                smsFeedDb.MessageText = q.messageText

        if not smsFeedDb.PhoneNumber:
            raise InputError(Ref(_('Not enough info for a message'),))

        try:
            self.session().add(smsFeedDb)
            self.session().flush((smsFeedDb,))

        except SQLAlchemyError as e:
            handle(e, smsFeedDb)

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
