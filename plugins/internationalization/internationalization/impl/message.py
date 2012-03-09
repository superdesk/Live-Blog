'''
Created on Mar 5, 2012

@package: internationalization
@copyright: 2011 Sourcefabric o.p.s.
@license: http://www.gnu.org/licenses/gpl-3.0.txt
@author: Gabriel Nistor

Implementation for the message API.
'''

from ..api.message import IMessageService
from ..meta.message import Message, QMessage
from ally.exception import InputException, Ref
from ally.internationalization import _
from ally.support.sqlalchemy.mapper import addLoadListener, addInsertListener, \
    addUpdateListener
from sql_alchemy.impl.entity import EntityGetCRUDServiceAlchemy
from internationalization.meta.source import Source

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

    def getMessages(self, sourceId=None, offset=None, limit=None, q=None):
        '''
        @see: IMessageService.getMessages
        '''
        if sourceId: filter = Message.Source == sourceId
        else: filter = None
        return self._getAll(filter, q, offset, limit)

    def getMessagesCount(self, sourceId=None, q=None):
        '''
        @see: IMessageService.getMessagesCount
        '''
        if sourceId: filter = Message.Source == sourceId
        else: filter = None
        return self._getCount(filter, q)

    def getComponentMessages(self, component, offset=None, limit=None, q=None):
        '''
        @see: IMessageService.getComponentMessages
        '''
        sqlQuery = self.session().query(Message).join(Source)
        return self._getAll(Source.Component == component, q, offset, limit, sqlQuery)

    def getComponentMessagesCount(self, component, q=None):
        '''
        @see: IMessageService.getComponentMessagesCount
        '''
        sqlQuery = self.session().query(Message).join(Source)
        return self._getCount(Source.Component == component, sqlQuery)

    def getPluginMessages(self, plugin, offset=None, limit=None, q=None):
        '''
        @see: IMessageService.getPluginMessages
        '''
        sqlQuery = self.session().query(Message).join(Source)
        return self._getAll(Source.Plugin == plugin, q, offset, limit, sqlQuery)

    def getPluginMessagesCount(self, plugin, q=None):
        '''
        @see: IMessageService.getPluginMessagesCount
        '''
        sqlQuery = self.session().query(Message).join(Source)
        return self._getCount(Source.Plugin == plugin, sqlQuery)

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
                raise InputException(Ref(_('Only a maximum of four plural forms is accepted, got %(nplurals)i') %
                                         dict(nplurals=len(message.Plural))))
            for k, plural in enumerate(message.Plural, 1):
                setattr(message, 'plural%s' % k, plural)
