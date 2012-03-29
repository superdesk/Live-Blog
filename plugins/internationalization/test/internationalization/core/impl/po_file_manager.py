'''
Created on Mar 27, 2012

@package support - cdm
@copyright 2012 Sourcefabric o.p.s.
@license http: // www.gnu.org / licenses / gpl - 3.0.txt
@author: Mugur Rus

Provides unit testing for the PO file manager.
'''

import unittest
from tempfile import NamedTemporaryFile, TemporaryDirectory
from os.path import join, dirname, isfile, isdir
from shutil import rmtree
from os import makedirs, remove, sep
from cdm.spec import PathNotFound

from internationalization.core.impl.po_file_manager import POFileManagerDB
from internationalization.api.message import IMessageService, Message
from internationalization.api.source import ISourceService, Source
from datetime import datetime

class TestMessageService(IMessageService):
    '''
    '''
    _components = 3

    _componentMessages = 5

    _plugins = 3

    _pluginMessages = 8

    def getMessagesCount(self, sourceId, q):
        '''
        Provides the total count of messages searched based on the given parameters.
        '''
        return self._components * self._componentMessages + self._plugins * self._pluginMessages

    def getMessages(self, sourceId, offset, limit, q):
        '''
        Provides the messages searched based on the given parameters.
        '''
        messages = []
        for c in range(self._components):
            messages.extend(self.getComponentMessages(c))
        for p in range(self._plugins):
            messages.extend(self.getPluginMessages(p))
        return messages

    def getComponentMessagesCount(self, component, q):
        '''
        Provides the total count of messages for the given component.
        '''
        return self._componentMessages

    def getComponentMessages(self, component, offset, limit, q):
        '''
        Provides the messages for the given component.
        '''
        messages = []
        for m in range(self._componentMessages):
            msg = Message()
            if m > 2:
                msg.Id = 'component %i message %i' % component, m
                msg.Context = 'component'
            else:
                msg.Id = 'message %i' % m
                msg.Context = ''
            msg.Source = 'src/component%i.py' % m
            msg.LineNumber = 100 + 2 * m
            messages.append(msg)
        return messages

    def getPluginMessagesCount(self, plugin, q):
        '''
        Provides the total count of messages for the given plugin.
        '''
        return self._pluginMessages

    def getPluginMessages(self, plugin, offset, limit, q):
        '''
        Provides the messages for the given plugin.
        '''
        messages = []
        for m in range(self._pluginMessages):
            msg = Message()
            if m > 3:
                msg.Id = 'plugin %i message %i' % plugin, m
                msg.Context = 'plugin'
            else:
                msg.Id = 'message %i' % m
                msg.Context = ''
            msg.Source = 'src/plugin%i.py' % m
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
        src.LastModified = datetime.now()
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
        src = poManager.sourceService.getAll()[0]
        print(src)

if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.testName']
    unittest.main()
