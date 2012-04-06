'''
Created on Mar 27, 2012

@package support - cdm
@copyright 2012 Sourcefabric o.p.s.
@license http: // www.gnu.org / licenses / gpl - 3.0.txt
@author: Mugur Rus

Provides unit testing for the PO file manager.
'''

from datetime import datetime
import unittest
from tempfile import NamedTemporaryFile, TemporaryDirectory
from os.path import join, dirname, isfile, isdir, abspath
from shutil import rmtree
from os import makedirs, remove, sep
from cdm.spec import PathNotFound
from babel.messages.pofile import read_po, write_po

from internationalization.api.message import IMessageService, Message
from internationalization.api.source import ISourceService, Source
from internationalization.core.impl.po_file_manager import POFileManagerDB


class TestMessageService(IMessageService):
    _componentStartId = 0

    _components = 3

    _componentMessages = 5

    _pluginStartId = 10000

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
            msg.Id = self._componentStartId + int(component) * self._componentMessages + m
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
            msg.Id = self._pluginStartId + int(plugin) * self._pluginMessages + m
            if m > 3:
                msg.Singular = 'plugin %s message %d' % (plugin, m)
                msg.Context = 'plugin'
            else:
                msg.Singular = 'message %i' % m
                msg.Context = ''
            msg.Source = int(plugin) + 10
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
        if id < 10:
            src.Component = str(id)
            src.Path = 'component_%d/src.py' % id
        else:
            src.Plugin = str(id)
            src.Path = 'plugin_%d/src.py' % id
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
        poManager.locale_dir_path = dirname(abspath(__file__))

        srcService = TestSourceService()
        self.assertEqual(srcService.getAll()[0].LastModified,
                         poManager.getGlobalPOTimestamp())
        self.assertEqual(srcService.getAll()[0].LastModified,
                         poManager.getComponentPOTimestamp('1'))
        self.assertEqual(srcService.getAll()[0].LastModified,
                         poManager.getPluginPOTimestamp('1'))

        poFile = poManager.getGlobalPOFile(); poFile.seek(0)
        globalTestCat = read_po(poFile)

        with open(join(dirname(abspath(__file__)), 'global-template.po')) as f:
            globalCat = read_po(f)

        self.assertEqual(len(globalCat), len(globalTestCat))
        for msg in globalCat:
            if msg and msg.id != '':
                self.assertEqual(msg, globalTestCat.get(msg.id, msg.context))

        poFile = poManager.getComponentPOFile('1'); poFile.seek(0)
        componentTestCat = read_po(poFile)

        with open(join(dirname(abspath(__file__)), 'component-template.po')) as f:
            componentCat = read_po(f)

        self.assertEqual(len(componentCat), len(componentTestCat))
        for msg in componentCat:
            if msg and msg.id != '':
                self.assertEqual(msg, componentTestCat.get(msg.id, msg.context))

        poFile = poManager.getPluginPOFile('1'); poFile.seek(0)
        pluginTestCat = read_po(poFile)

        with open(join(dirname(abspath(__file__)), 'plugin-template.po')) as f:
            pluginCat = read_po(f)

        self.assertEqual(len(pluginCat), len(pluginTestCat))
        for msg in pluginCat:
            if msg and msg.id != '':
                self.assertEqual(msg, pluginTestCat.get(msg.id, msg.context))

        with open(join(dirname(abspath(__file__)), 'global-_ro.po')) as f:
            poManager.updateGlobalPOFile(f, 'ro')

        with open(join(dirname(abspath(__file__)), 'component 1_ro.po')) as f:
            poManager.updateComponentPOFile(f, '1', 'ro')

#        with open(join(dirname(abspath(__file__)), 'plugin 1_ro.po')) as f:
#            poManager.updatePluginPOFile(f, '1', 'ro')

#        tmpFile = NamedTemporaryFile()
#        tmpFile.delete = False
#        print(tmpFile.name)
#
#        write_po(tmpFile, pluginTestCat)

if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.testName']
    unittest.main()
