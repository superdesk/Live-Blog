'''
Created on Mar 27, 2012

@package support - cdm
@copyright 2012 Sourcefabric o.p.s.
@license http: // www.gnu.org / licenses / gpl - 3.0.txt
@author: Mugur Rus

Provides unit testing for the PO file manager.
'''

# Required in order to register the package extender whenever the unit test is run.
if True:
    import package_extender
    package_extender.PACKAGE_EXTENDER.setForUnitTest(True)

# --------------------------------------------------------------------

from babel.messages.pofile import read_po
from datetime import datetime
from internationalization.api.message import IMessageService, Message
from internationalization.api.source import ISourceService, Source
from internationalization.core.impl.po_file_manager import POFileManager
from internationalization.support.babel.util_babel import msgId
from os.path import join, dirname, abspath
from tempfile import TemporaryDirectory
import unittest

# --------------------------------------------------------------------

class TestMessageService(IMessageService):
    _componentStartId = 0

    _components = 3

    _componentMessages = 5

    _pluginStartId = 10000

    _plugins = 3

    _pluginMessages = 8

    def getMessagesCount(self, sourceId=None, qm=None, qs=None):
        '''
        Provides the total count of messages searched based on the given parameters.
        '''
        return self._components * self._componentMessages + self._plugins * self._pluginMessages

    def getMessages(self, sourceId=None, offset=None, limit=None, qm=None, qs=None):
        '''
        Provides the messages searched based on the given parameters.
        '''
        messages = []
        for c in range(self._components):
            messages.extend(self.getComponentMessages(str(c)))
        for p in range(self._plugins):
            messages.extend(self.getPluginMessages(str(p)))
        return messages

    def getComponentMessagesCount(self, component, qm=None, qs=None):
        '''
        Provides the total count of messages for the given component.
        '''
        return self._componentMessages

    def getComponentMessages(self, component, offset=None, limit=None, qm=None, qs=None):
        '''
        Provides the messages for the given component.
        '''
        messages = []
        for m in range(self._componentMessages):
            if qs and m % 2: continue
            msg = Message()
            msg.Id = self._componentStartId + int(component) * self._componentMessages + m
            if m > 2:
                msg.Singular = 'component %s message %d' % (component, m)
                msg.Plural = None if m % 2 else ['component %s message %d plural' % (component, m)]
                msg.Context = 'component'
            else:
                msg.Singular = 'message %i' % m
                msg.Plural = None if m % 2 else ['message %d plural' % m]
                msg.Context = ''
            msg.Source = int(component)
            msg.LineNumber = 100 + m
            messages.append(msg)
        return messages

    def getPluginMessagesCount(self, plugin, qm=None, qs=None):
        '''
        Provides the total count of messages for the given plugin.
        '''
        return self._pluginMessages

    def getPluginMessages(self, plugin, offset=None, limit=None, qm=None, qs=None):
        '''
        Provides the messages for the given plugin.
        '''
        messages = []
        for m in range(self._pluginMessages):
            if qs and m % 2: continue
            msg = Message()
            msg.Id = self._pluginStartId + int(plugin) * self._pluginMessages + m
            if m > 3:
                msg.Singular = 'plugin %s message %d' % (plugin, m)
                msg.Plural = None if m % 2 else ['plugin %s message %d plural' % (plugin, m)]
                msg.Context = 'plugin'
            else:
                msg.Singular = 'message %i' % m
                msg.Plural = None if m % 2 else ['message %d plural' % m]
                msg.Context = ''
            msg.Source = 10 + int(plugin)
            msg.LineNumber = 200 + m
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
        ext = 'py' if id % 2 else 'js'
        if id < 10:
            src.Component = str(id)
            src.Path = 'component_%d/src.%s' % (id, ext)
        else:
            src.Plugin = str(id)
            src.Path = 'plugin_%d/src.%s' % (id, ext)
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
    _poDir = join(dirname(abspath(__file__)), 'po')

    def testLocalFilesystemCDM(self):
        poManager = POFileManager()
        poManager.messageService = TestMessageService()
        poManager.sourceService = TestSourceService()
        poRepDir = TemporaryDirectory()
        poManager.locale_dir_path = poRepDir.name

        # ********************************************
        # test updateGlobalPOFile
        with open(join(self._poDir, 'global_ro.po')) as f:
            globalCat = read_po(f); f.seek(0)
            poManager.updateGlobalPOFile('ro', f)
        with open(join(poManager.locale_dir_path, 'global_ro.po')) as f:
            globalTestCat = read_po(f)
        self.assertEqual(len(globalCat), len(globalTestCat))
        for msg in globalCat:
            if msg and msg.id:
                self.assertEqual(msg.string, globalTestCat.get(msgId(msg), msg.context).string)

        # ********************************************
        # test updateComponentPOFile
        with open(join(self._poDir, 'component 1_ro.po')) as f:
            componentCat = read_po(f); f.seek(0)
            poManager.updateComponentPOFile('1', 'ro', f)
        with open(join(poManager.locale_dir_path, 'component', '1_ro.po')) as f:
            componentTestCat = read_po(f)
        for msg in componentTestCat:
            if msg and msg.id:
                self.assertEqual(msg.string, componentCat.get(msgId(msg), msg.context).string)
                self.assertNotEqual(msg.string, globalCat.get(msgId(msg), msg.context).string)

        # ********************************************
        # test updatePluginPOFile
        with open(join(self._poDir, 'plugin 1_ro.po')) as f:
            pluginCat = read_po(f); f.seek(0)
            poManager.updatePluginPOFile('1', 'ro', f)
        with open(join(poManager.locale_dir_path, 'plugin', '1_ro.po')) as f:
            pluginTestCat = read_po(f)
        for msg in pluginTestCat:
            if msg and msg.id:
                self.assertEqual(msg.string, pluginCat.get(msgId(msg), msg.context).string)
                self.assertNotEqual(msg.string, globalCat.get(msgId(msg), msg.context).string)

        # ********************************************
        # test getGlobalPOFile
        poFile = poManager.getGlobalPOFile('ro')
        globalTestCat = read_po(poFile)
        self.assertEqual(len(globalCat), len(globalTestCat))
        self._checkHeader(globalTestCat, globalCat)
        for msg in globalCat:
            if msg and msg.id:
                self.assertEqual(msg.locations, globalTestCat.get(msgId(msg), msg.context).locations)
                self.assertEqual(msg.string, globalTestCat.get(msgId(msg), msg.context).string)

        # ********************************************
        # test getComponentPOFile
        poFile = poManager.getComponentPOFile('1', 'ro')
        componentTestCat = read_po(poFile)
        self.assertEqual(len(componentCat), len(componentTestCat))
        self._checkHeader(componentTestCat, componentCat)
        for msg in componentCat:
            if msg and msg.id:
                self.assertEqual(msg.locations, componentTestCat.get(msgId(msg), msg.context).locations)
                self.assertEqual(msg.string, componentTestCat.get(msg.id, msg.context).string)

        # ********************************************
        # test getPluginPOFile
        poFile = poManager.getPluginPOFile('1', 'ro')
        pluginTestCat = read_po(poFile)
        self.assertEqual(len(pluginCat), len(pluginTestCat))
        self._checkHeader(pluginTestCat, pluginCat)
        for msg in pluginCat:
            if msg and msg.id:
                self.assertEqual(msg.locations, pluginTestCat.get(msgId(msg), msg.context).locations)
                self.assertEqual(msg.string, pluginTestCat.get(msg.id, msg.context).string)

        # ********************************************
        # test getGlobalAsDict
#        globalTestDict = poManager.getGlobalAsDict('ro')
#        for domain, messages in globalTestDict.items():
#            print('domain: %s' % domain)
#            for id, plurals in messages.items():
#                print('    %s -> %s' % (id, plurals))

        # ********************************************
        # test getComponentPOFile
#        componentTestDict = poManager.getComponentAsDict('1', 'ro')
#        print(componentTestDict)

        # ********************************************
        # test getComponentPOFile
#        pluginTestDict = poManager.getPluginAsDict('1', 'ro')
#        print(pluginTestDict)

    def _checkHeader(self, testCat, witnessCat):
        self.assertEqual(testCat.domain, witnessCat.domain)
        self.assertEqual(testCat.locale, witnessCat.locale)
        self.assertEqual(testCat.project, witnessCat.project)
        self.assertEqual(testCat.version, witnessCat.version)
        self.assertEqual(testCat.copyright_holder, witnessCat.copyright_holder)
        self.assertEqual(testCat.msgid_bugs_address, witnessCat.msgid_bugs_address)
        self.assertEqual(testCat.last_translator, witnessCat.last_translator)
        self.assertEqual(testCat.language_team, witnessCat.language_team)
        self.assertEqual(testCat.charset, witnessCat.charset)
        self.assertEqual(testCat.fuzzy, witnessCat.fuzzy)

if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.testName']
    unittest.main()
