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
from ally.api.extension import IterPart

# --------------------------------------------------------------------

@injected
@setup(IMessageService)
class MessageServiceAlchemy(EntityGetCRUDServiceAlchemy, IMessageService):
    '''
    Alchemy implementation for @see: IMessageService
    '''

    def __init__(self):
        EntityGetCRUDServiceAlchemy.__init__(self, Message, QMessage)

    def getMessages(self, sourceId=None, offset=None, limit=None, detailed=False, qm=None, qs=None):
        '''
        @see: IMessageService.getMessages
        '''
        sql = self.session().query(Message)
        if sourceId: sql = sql.filter(Message.Source == sourceId)
        if qm: sql = buildQuery(sql, qm, Message)
        if qs: sql = buildQuery(sql.join(Source), qs, Source)
        sqlLimit = buildLimits(sql, offset, limit)
        if detailed: return IterPart(sqlLimit.all(), sql.count(), offset, limit)
        return sqlLimit.all()

    def getComponentMessages(self, component, offset=None, limit=None, detailed=False, qm=None, qs=None):
        '''
        @see: IMessageService.getComponentMessages
        '''
        sql = self.session().query(Message).join(Source).filter(Source.Component == component)
        if qm: sql = buildQuery(sql, qm, Message)
        if qs: sql = buildQuery(sql, qs, Source)
        sqlLimit = buildLimits(sql, offset, limit)
        if detailed: return IterPart(sqlLimit.all(), sql.count(), offset, limit)
        return sqlLimit.all()

    def getPluginMessages(self, plugin, offset=None, limit=None, detailed=False, qm=None, qs=None):
        '''
        @see: IMessageService.getPluginMessages
        '''
        sql = self.session().query(Message).join(Source).filter(Source.Plugin == plugin)
        if qm: sql = buildQuery(sql, qm, Message)
        if qs: sql = buildQuery(sql, qs, Source)
        sqlLimit = buildLimits(sql, offset, limit)
        if detailed: return IterPart(sqlLimit.all(), sql.count(), offset, limit)
        return sqlLimit.all()
