'''
Created on Mar 27, 2012

@package support - cdm
@copyright 2012 Sourcefabric o.p.s.
@license http: // www.gnu.org / licenses / gpl - 3.0.txt
@author: Mugur Rus

Provides unit testing for the PO file manager.
'''

from datetime import datetime
from internationalization.api.message import IMessageService, Message
from internationalization.api.source import ISourceService, Source
from internationalization.core.impl.po_file_manager import POFileManagerDB
from tempfile import TemporaryDirectory
import unittest

class TestMessageService(IMessageService):
    '''
    '''
    _components = 3

    _componentMessages = 5

    _plugins = 3

    _pluginMessages = 8

    def getMessagesCount(self, sourceId=None, q=None):
        '''
        Provides the total count of messages searched based on the given parameters.
        '''
        return self._components * self._componentMessages + self._plugins * self._pluginMessages

    def getMessages(self, sourceId=None, offset=None, limit=None, q=None):
        '''
        Provides the messages searched based on the given parameters.
        '''
        messages = []
        for c in range(self._components):
            messages.extend(self.getComponentMessages(str(c)))
        for p in range(self._plugins):
            messages.extend(self.getPluginMessages(str(p)))
        return messages

    def getComponentMessagesCount(self, component, q=None):
        '''
        Provides the total count of messages for the given component.
        '''
        return self._componentMessages

    def getComponentMessages(self, component, offset=None, limit=None, q=None):
        '''
        Provides the messages for the given component.
        '''
        messages = []
        for m in range(self._componentMessages):
            msg = Message()
            msg.Id = int(component) * 10 + m
            if m > 2:
                msg.Singular = 'component %s message %d' % (component, m)
                msg.Context = 'component'
            else:
                msg.Singular = 'message %i' % m
                msg.Context = ''
            msg.Source = int(component)
            msg.LineNumber = 100 + 2 * m
            messages.append(msg)
        return messages

    def getPluginMessagesCount(self, plugin, q=None):
        '''
        Provides the total count of messages for the given plugin.
        '''
        return self._pluginMessages

    def getPluginMessages(self, plugin, offset=None, limit=None, q=None):
        '''
        Provides the messages for the given plugin.
        '''
        messages = []
        for m in range(self._pluginMessages):
            msg = Message()
            msg.Id = int(plugin) * 10 + m
            if m > 3:
                msg.Singular = 'plugin %s message %d' % (plugin, m)
                msg.Context = 'plugin'
            else:
                msg.Singular = 'message %i' % m
                msg.Context = ''
            msg.Source = int(plugin)
            msg.LineNumber = 100 + 2 * m
            messages.append(msg)
        return messages

    def getById(self, id):
        msg = Message()
        msg.Id = id
        return msg

    def insert(self, entity):
        pass

    def update(self, entity):
        pass

    def delete(self, id):
        pass


class TestSourceService(ISourceService):
    def getById(self, id):
        src = Source()
        src.Id = id
        return src

    def getAll(self, offset=None, limit=None, q=None):
        src = Source()
        src.LastModified = datetime(2012, 4, 1, 12, 15, 10)
        return [src]

    def insert(self, entity):
        pass

    def update(self, entity):
        pass

    def delete(self, id):
        pass


class TestHTTPDelivery(unittest.TestCase):

    def testLocalFilesystemCDM(self):
        poManager = POFileManagerDB()
        poManager.messageService = TestMessageService()
        poManager.sourceService = TestSourceService()
        poRepDir = TemporaryDirectory()
        poManager.locale_dir_path = poRepDir.name

        srcService = TestSourceService()
        self.assertEqual(srcService.getAll()[0].LastModified,
                         poManager.getGlobalPOTimestamp())
        self.assertEqual(srcService.getAll()[0].LastModified,
                         poManager.getComponentPOTimestamp('1'))
        self.assertEqual(srcService.getAll()[0].LastModified,
                         poManager.getPluginPOTimestamp('1'))

        poFile = poManager.getGlobalPOFile()
        print(poFile)

        src = poManager.sourceService.getAll()[0]
        print(src)

if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.testName']
    unittest.main()
