'''
Created on Mar 9, 2012

@package: internationalization
@copyright: 2012 Sourcefabric o.p.s.
@license: http://www.gnu.org/licenses/gpl-3.0.txt
@author: Mugur Rus

Implementation for the PO file management.
'''

from ally.internationalization import _
from internationalization.api.POFile import IPOFileService
from babel.messages.catalog import Catalog
from internationalization.api.message import IMessageService
from ally.container import wire
from ally.container.ioc import injected

# --------------------------------------------------------------------

@injected
class POFileServiceAlchemy(IPOFileService):
    '''
    Implementation for @see: IPOService
    '''

    messageService = IMessageService; wire.entity('messageService')

    def __init__(self):
        assert isinstance(self.messageService, IMessageService), 'Invalid message service %s' % self.messageService

    def getGlobalPOFile(self, language=None):
        '''
        @see: IPOService.getGlobalPOFile
        '''
        messages = self.messageService.getMessages()
        catalog = self._buildCatalog(messages)

    def getComponentPOFile(self, component):
        '''
        @see: IPOService.getComponentPOFile
        '''
        messages = self.messageService.getComponentMessages(component)
        catalog = self._buildCatalog(messages)

    def getPluginPOFile(self, plugin):
        '''
        @see: IPOService.getPluginPOFile
        '''
        messages = self.messageService.getPluginMessages(plugin)
        catalog = self._buildCatalog(messages)

    def _buildCatalog(self, messages):
        catalog = Catalog()
        for msg in messages:
            msgId = msg.Singular if not msg.Plural else (msg.Singular,) + msg.Plural
            catalog.add(id=msgId, locations=((msg.Source.Path, msg.LineNumber),), flags=(),
                        auto_comments=(msg.Comments), user_comments=(), context=msg.Context)
        return catalog
