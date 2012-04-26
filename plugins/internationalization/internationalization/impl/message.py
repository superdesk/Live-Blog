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
from internationalization.meta.source import Source
from sql_alchemy.impl.entity import EntityGetCRUDServiceAlchemy

# --------------------------------------------------------------------

class MessageServiceAlchemy(EntityGetCRUDServiceAlchemy, IMessageService):
    '''
    Alchemy implementation for @see: IMessageService
    '''

    def __init__(self):
        EntityGetCRUDServiceAlchemy.__init__(self, Message, QMessage)

    def getMessagesCount(self, sourceId=None, q=None):
        '''
        @see: IMessageService.getMessagesCount
        '''
        if sourceId: filter = Message.Source == sourceId
        else: filter = None
        return self._getCount(filter, q)

    def getMessages(self, sourceId=None, offset=None, limit=None, q=None):
        '''
        @see: IMessageService.getMessages
        '''
        if sourceId: filter = Message.Source == sourceId
        else: filter = None
        return self._getAll(filter, q, offset, limit)

    def getComponentMessagesCount(self, component, q=None):
        '''
        @see: IMessageService.getComponentMessagesCount
        '''
        sqlQuery = self.session().query(Message).join(Source)
        return self._getCount(Source.Component == component, sqlQuery)

    def getComponentMessages(self, component, offset=None, limit=None, q=None):
        '''
        @see: IMessageService.getComponentMessages
        '''
        sqlQuery = self.session().query(Message).join(Source)
        return self._getAll(Source.Component == component, q, offset, limit, sqlQuery)

    def getPluginMessagesCount(self, plugin, q=None):
        '''
        @see: IMessageService.getPluginMessagesCount
        '''
        sqlQuery = self.session().query(Message).join(Source)
        return self._getCount(Source.Plugin == plugin, sqlQuery)

    def getPluginMessages(self, plugin, offset=None, limit=None, q=None):
        '''
        @see: IMessageService.getPluginMessages
        '''
        sqlQuery = self.session().query(Message).join(Source)
        return self._getAll(Source.Plugin == plugin, q, offset, limit, sqlQuery)
