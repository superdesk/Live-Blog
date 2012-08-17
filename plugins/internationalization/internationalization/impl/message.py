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
from ally.container.ioc import injected
from ally.container.support import setup
from internationalization.meta.source import Source
from sql_alchemy.impl.entity import EntityGetCRUDServiceAlchemy
from ally.support.sqlalchemy.util_service import buildQuery, buildLimits

# --------------------------------------------------------------------

@injected
@setup(IMessageService)
class MessageServiceAlchemy(EntityGetCRUDServiceAlchemy, IMessageService):
    '''
    Alchemy implementation for @see: IMessageService
    '''

    def __init__(self):
        EntityGetCRUDServiceAlchemy.__init__(self, Message, QMessage)

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
