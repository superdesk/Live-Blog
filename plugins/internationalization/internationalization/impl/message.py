'''
Created on Mar 5, 2012

@package: internationalization
@copyright: 2011 Sourcefabric o.p.s.
@license: http://www.gnu.org/licenses/gpl-3.0.txt
@author: Gabriel Nistor

Implementation for the message API.
'''

from ..api.message import IMessageService, QMessage
from ..meta.message import Message
from ally.exception import InputError, Ref
from ally.internationalization import _
from ally.support.sqlalchemy.mapper import addLoadListener, addInsertListener, \
    addUpdateListener
from sql_alchemy.impl.entity import EntityGetCRUDServiceAlchemy
from internationalization.meta.source import Source
from ally.support.sqlalchemy.util_service import buildQuery, buildLimits

# --------------------------------------------------------------------

class MessageServiceAlchemy(EntityGetCRUDServiceAlchemy, IMessageService):
    '''
    Alchemy implementation for @see: IMessageService
    '''

    def __init__(self):
        EntityGetCRUDServiceAlchemy.__init__(self, Message, QMessage)
        addLoadListener(Message, self._onLoadMessage)
        addInsertListener(Message, self._onPersistMessage)
        addUpdateListener(Message, self._onPersistMessage)

    def getMessagesCount(self, sourceId=None, qm=None, qs=None):
        '''
        @see: IMessageService.getMessagesCount
        '''
        sqlQuery = self.session().query(Message)
        if sourceId: sqlQuery = sqlQuery.filter(Message.Source == sourceId)
        if qm: sqlQuery = buildQuery(sqlQuery, qm, Message)
        if qs: sqlQuery = buildQuery(sqlQuery.join(Source), qs, Source)
        return sqlQuery.count()

    def getMessages(self, sourceId=None, offset=None, limit=None, qm=None, qs=None):
        '''
        @see: IMessageService.getMessages
        '''
        sqlQuery = self.session().query(Message)
        if sourceId: sqlQuery = sqlQuery.filter(Message.Source == sourceId)
        if qm: sqlQuery = buildQuery(sqlQuery, qm, Message)
        if qs: sqlQuery = buildQuery(sqlQuery.join(Source), qs, Source)
        sqlQuery = buildLimits(sqlQuery, offset, limit)
        return sqlQuery.all()

    def getComponentMessagesCount(self, component, qm=None, qs=None):
        '''
        @see: IMessageService.getComponentMessagesCount
        '''
        sqlQuery = self.session().query(Message).join(Source).filter(Source.Component == component)
        if qm: sqlQuery = buildQuery(sqlQuery, qm, Message)
        if qs: sqlQuery = buildQuery(sqlQuery, qs, Source)
        return sqlQuery.count()

    def getComponentMessages(self, component, offset=None, limit=None, qm=None, qs=None):
        '''
        @see: IMessageService.getComponentMessages
        '''
        sqlQuery = self.session().query(Message).join(Source).filter(Source.Component == component)
        if qm: sqlQuery = buildQuery(sqlQuery, qm, Message)
        if qs: sqlQuery = buildQuery(sqlQuery, qs, Source)
        sqlQuery = buildLimits(sqlQuery, offset, limit)
        return sqlQuery.all()

    def getPluginMessagesCount(self, plugin, qm=None, qs=None):
        '''
        @see: IMessageService.getPluginMessagesCount
        '''
        sqlQuery = self.session().query(Message).join(Source).filter(Source.Plugin == plugin)
        if qm: sqlQuery = buildQuery(sqlQuery, qm, Message)
        if qs: sqlQuery = buildQuery(sqlQuery, qs, Source)
        return sqlQuery.count()

    def getPluginMessages(self, plugin, offset=None, limit=None, qm=None, qs=None):
        '''
        @see: IMessageService.getPluginMessages
        '''
        sqlQuery = self.session().query(Message).join(Source).filter(Source.Plugin == plugin)
        if qm: sqlQuery = buildQuery(sqlQuery, qm, Message)
        if qs: sqlQuery = buildQuery(sqlQuery, qs, Source)
        sqlQuery = buildLimits(sqlQuery, offset, limit)
        return sqlQuery.all()

    # ----------------------------------------------------------------

    def _onLoadMessage(self, message):
        '''
        Called when a message is loaded.
        '''
        assert isinstance(message, Message), 'Invalid message %s' % message
        plurals = [plural for plural in (getattr(message, 'plural%s' % k) for k in range(1, 5)) if plural is not None]
        if plurals: message.Plural = plurals

    def _onPersistMessage(self, message):
        '''
        Called when a message is persisted.
        '''
        assert isinstance(message, Message), 'Invalid message %s' % message
        if message.Plural:
            if len(message.Plural) > 4:
                raise InputError(Ref(_('Only a maximum of four plural forms is accepted, got %(nplurals)i') %
                                     dict(nplurals=len(message.Plural))))
            for k, plural in enumerate(message.Plural, 1):
                setattr(message, 'plural%s' % k, plural)
