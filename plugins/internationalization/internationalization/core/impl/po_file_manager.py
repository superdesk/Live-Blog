'''
Created on Mar 13, 2012

@package: internationalization
@copyright: 2012 Sourcefabric o.p.s.
@license: http://www.gnu.org/licenses/gpl-3.0.txt
@author: Mugur Rus

Implementation for the PO file management.
'''

import os
from genericpath import isdir, isfile
from os.path import dirname, join
from io import BytesIO
from datetime import datetime
from babel import localedata, core
from babel.messages.catalog import Catalog
from babel.messages.mofile import write_mo
from babel.messages.pofile import read_po, write_po
from babel.util import odict

from ally.api.type import Iter
from ally.container import wire
from ally.container.ioc import injected
from introspection.api.component import Component
from introspection.api.plugin import Plugin
from cdm.spec import PathNotFound
from internationalization.api.message import IMessageService
from internationalization.api.source import ISourceService, QSource
from internationalization.api.message import Message
from internationalization.core.spec import IPOFileManager

# --------------------------------------------------------------------

# Babel FIX: We need to adjust the dir name for locales since they need to be outside the .egg file
localedata._dirname = localedata._dirname.replace('.egg', '')
core._filename = core._filename.replace('.egg', '')

@injected
class POFileManagerDB(IPOFileManager):
    '''
    Implementation for @see: IPOFileManager
    '''

    messageService = IMessageService; wire.entity('messageService')

    sourceService = ISourceService; wire.entity('sourceService')

    locale_dir_path = str; wire.config('locale_dir_path', doc=
                                       'The locale repository path')

    def __init__(self):
        assert isinstance(self.messageService, IMessageService), 'Invalid message service %s' % self.messageService
        assert isinstance(self.sourceService, ISourceService), 'Invalid source file service %s' % self.sourceService
        assert isinstance(self.locale_dir_path, str), 'Invalid locale directory %s' % self.locale_dir_path
        if not isdir(self.locale_dir_path) or not os.access(self.locale_dir_path, os.W_OK):
            raise Exception('Unable to access the repository directory %s' % self.locale_dir_path)

    def getGlobalPOTimestamp(self, locale=None):
        return self._poFileTimestamp(locale=locale)

    def getComponentPOTimestamp(self, component, locale=None):
        return self._poFileTimestamp(component=component, locale=locale)

    def getPluginPOTimestamp(self, plugin, locale=None):
        return self._poFileTimestamp(plugin=plugin, locale=locale)

    def getGlobalPOFile(self, locale=None):
        '''
        @see: IPOFileManager.getGlobalPOFile
        '''
        assert not locale or isinstance(locale, str), 'Invalid locale %s' % locale
        template = self._buildCatalog(self.messageService.getMessages(), locale)
        if locale:
            self._updateFile(None, None, locale, None, template)
        return self._buildPOFile(locale, template)

    def getComponentPOFile(self, component, locale=None):
        '''
        @see: IPOFileManager.getComponentPOFile
        '''
        assert not locale or isinstance(locale, str), 'Invalid locale %s' % locale
        template = self._buildCatalog(self.messageService.getComponentMessages(component), locale)
        if locale:
            try:
                exceptionsCatalog = self._readPOFile(self._filePath(locale, component)['po'], locale)
            except PathNotFound:
                exceptionsCatalog = Catalog(locale)
            self._processPOFile(component, None, locale, exceptionsCatalog)
            exceptionsCatalog = self._readPOFile(self._filePath(locale, component)['po'], locale)
        else:
            exceptionsCatalog = Catalog(locale)
        return self._buildPOFile(locale, template, exceptionsCatalog)

    def getPluginPOFile(self, plugin, locale=None):
        '''
        @see: IPOFileManager.getPluginPOFile
        '''
        assert not locale or isinstance(locale, str), 'Invalid locale %s' % locale
        template = self._buildCatalog(self.messageService.getPluginMessages(plugin), locale)
        if locale:
            try:
                exceptionsCatalog = self._readPOFile(self._filePath(locale, plugin=plugin)['po'], locale)
            except PathNotFound:
                exceptionsCatalog = Catalog(locale)
            self._processPOFile(None, plugin, locale, exceptionsCatalog)
            exceptionsCatalog = self._readPOFile(self._filePath(locale, plugin=plugin)['po'], locale)
        else:
            exceptionsCatalog = Catalog(locale)
        return self._buildPOFile(locale, template, exceptionsCatalog)

    def updateGlobalPOFile(self, poFile, locale):
        '''
        @see: IPOFileManager.updateGlobalPOFile
        '''
        assert hasattr(poFile, 'read'), 'Invalid file object %s' % poFile
        assert isinstance(locale, str), 'Invalid locale %s' % locale
        keys = self.messageService.getMessages()
        templateCatalog = self._buildCatalog(keys, locale)
        self._updateFile(None, None, locale, read_po(poFile), templateCatalog)

    def updateComponentPOFile(self, poFile, component, locale):
        '''
        @see: IPOFileManager.updateComponentPOFile
        '''
        assert hasattr(poFile, 'read'), 'Invalid file object %s' % poFile
        assert isinstance(locale, str), 'Invalid locale %s' % locale
        poFile.seek(0)
        self._processPOFile(component, None, locale, read_po(poFile))

    def updatePluginPOFile(self, poFile, plugin, locale):
        '''
        @see: IPOFileManager.updatePluginPOFile
        '''
        assert hasattr(poFile, 'read'), 'Invalid file object %s' % poFile
        assert isinstance(locale, str), 'Invalid locale %s' % locale
        poFile.seek(0)
        self._processPOFile(None, plugin, locale, read_po(poFile))

    def _processPOFile(self, component, plugin, locale, newCatalog):
        if component:
            keys = self.messageService.getComponentMessages(component)
        elif plugin:
            keys = self.messageService.getPluginMessages(plugin)
        exceptTemplateCatalog = self._buildCatalog(keys, locale)
        exceptionsCatalog = Catalog(locale)
        keys = self.messageService.getMessages()
        globalTemplateCatalog = self._buildCatalog(keys, locale)
        try:
            globalCatalog = self._readPOFile(self._filePath(locale)['po'], locale)
        except PathNotFound:
            globalCatalog = globalTemplateCatalog

        for msg in newCatalog:
            if not msg or msg.id == '':
                continue
            globalMsg = globalCatalog.get(msg.id, msg.context)
            if not globalMsg:
                continue
            excMsg = exceptTemplateCatalog.get(msg.id, msg.context)
            if not excMsg:
                continue
            if msg.string != globalMsg.string:
                exceptionsCatalog.add(msg.id, msg.string, msg.locations, msg.flags, msg.auto_comments,
                                      msg.user_comments, msg.previous_id, msg.lineno, msg.context)
            else:
                exceptTemplateCatalog.delete(msg.id, msg.context)
                globalCatalog.add(msg.id, msg.string, [], msg.flags, msg.auto_comments,
                                  msg.user_comments, msg.previous_id, msg.lineno, msg.context)

        self._updateFile(None, None, locale, globalCatalog, globalTemplateCatalog)
        self._updateFile(component, plugin, locale, None, exceptionsCatalog)

    def _poFileTimestamp(self, component:Component.Id=None, plugin:Plugin.Id=None, locale:str=None):
        '''
        @see: IPOFileManager.poFileTimestamp
        '''
        assert not locale or isinstance(locale, str), 'Invalid locale %s' % locale
        lastMsgTimestamp = self._messagesLastModified(component, plugin)
        if not locale:
            return lastMsgTimestamp
        path = self._filePath(locale, component, plugin)['po']
        if not isfile(path):
            return None
        fileMTime = datetime.fromtimestamp(os.stat(path).st_mtime)
        if fileMTime >= lastMsgTimestamp:
            return fileMTime
        else:
            return lastMsgTimestamp

    def _updateFile(self, component:Component.Id, plugin:Plugin.Id, locale:str, newCatalog:Catalog,
                    templateCatalog:Catalog):
        '''
        Update a PO file from the given file like object.

        @param component: Component.Id
            The component identifying the translation file.
        @param plugin: Plugin.Id
            The plugin identifying the translation file.
        @param newCatalog: Catalog
            Catalog containing the updates
        @param templateCatalog: Catalog
            Catalog containing allowed keys. Keys not existent in this catalog
            will be discarded from the PO file.
        '''
        if newCatalog:
            newCatalog.update(templateCatalog)
        else:
            newCatalog = templateCatalog

        paths = self._filePath(locale, component, plugin)
        try:
            catalog = self._readPOFile(paths['po'], locale)
            catalog.update(newCatalog)
        except PathNotFound:
            catalog = newCatalog
            catalog.obsolete = odict()

        if not isdir(dirname(paths['po'])):
            os.makedirs(dirname(paths['po']))
        with open(paths['po'], 'wb') as globalPo:
            write_po(globalPo, catalog)
        with open(paths['mo'], 'wb') as globalMo:
            write_mo(globalMo, catalog)

    def _buildPOFile(self, locale:str=None, templateCatalog:Catalog=None,
                     exceptionsCat:Catalog=None):
        '''
        Builds a PO file from the given file (as file object) to read from, for the
        given locale, using the given template and exceptions catalogs.
        Messages not in the template will be discarded while messages from the
        exceptions catalog will overwrite the messages with the same keys that
        existed in the given PO file.
        
        @param locale: str
            The locale code
        @param templateCatalog: Catalog
            The template catalog used to filter the messages. Only keys from this
            template will be kept in the catalog.
        @param exceptionsCat: Catalog
            Messages that override the generic translations.
        @return: file like object
            File like object that contains the PO file content
        '''
        if not templateCatalog:
            templateCatalog = Catalog(locale)
        if not exceptionsCat:
            exceptionsCat = Catalog(locale)
        try:
            globalCatalog = self._readPOFile(self._filePath(locale)['po'], locale)
        except PathNotFound:
            globalCatalog = Catalog(locale)
        for msg in globalCatalog:
            if not msg or msg.id == '':
                continue
            exceptionsCat.add(msg.id, msg.string, msg.locations, msg.flags, msg.auto_comments,
                              msg.user_comments, msg.id, msg.lineno, msg.context)
        exceptionsCat.update(templateCatalog)
        exceptionsCat.obsolete = odict()
        fileObj = BytesIO()
        write_po(fileObj, exceptionsCat)
        return fileObj

    def _readPOFile(self, path:str, locale:str=None) -> Catalog:
        '''
        Read the file pointed to by the given path into a catalog.

        @param path: str
        @param locale: str
            The locale code
        '''
        if not isfile(path):
            raise PathNotFound(path)
        with open(path) as fObj:
            return read_po(fObj, locale)

    def _fileName(self, locale:str=None, component:Component.Id=None, plugin:Plugin.Id=None):
        '''
        Returns the name of the PO file corresponding to the given locale and/or
        component / plugin. If no component of plugin was specified it returns the
        name of the global PO file.
        
        @param locale: str
            The locale code
        @param component: Component.Id
        @param plugin: Plugin.Id
        '''
        fileLocale = '_' + locale if locale else ''
        if component:
            name = 'component' + os.sep + component + fileLocale
        elif plugin:
            name = 'plugin' + os.sep + plugin + fileLocale
        else:
            name = 'global' + fileLocale
        return {'po':name + '.po', 'mo':name + '.mo'}

    def _filePath(self, locale:str=None, component:Component.Id=None, plugin:Plugin.Id=None):
        '''
        Returns the path to the internal PO file corresponding to the given locale and / or
        component / plugin. If no component of plugin was specified it returns the
        name of the global PO file.
        
        @param locale: str
            The locale code
        @param component: Component.Id
        @param plugin: Plugin.Id
        '''
        names = self._fileName(locale, component, plugin)
        return {'po':join(self.locale_dir_path, names['po']), 'mo':join(self.locale_dir_path, names['mo'])}

    def _messagesLastModified(self, component:Component.Id=None, plugin:Plugin.Id=None) -> datetime:
        '''
        Returns the timestamp of the last modified message from the messages table.

        @param component: Component.Id
            Filters by component
        @param plugin: Plugin.Id
            Filters by plugin
        @return: timestamp
        '''
        q = QSource()
        q.lastModified.orderDesc()
        if component:
            q.component = component
        elif plugin:
            q.plugin = plugin
        sources = self.sourceService.getAll(0, 1, q)
        if sources:
            return sources[0].LastModified
        return None

    def _buildCatalog(self, messages, locale:str=None) -> Catalog:
        '''
        Builds a catalog from the given messages list.
        
        @param messages: list of Message entities
        @param locale: str
            The locale code
        @return: Catalog
        '''
        assert isinstance(messages, Iter) or isinstance(messages, tuple) or isinstance(messages, list), \
                'Invalid messages list %s' % messages
        catalog = Catalog(locale)
        if isinstance(messages, Iter):
            messages = (messages,)
        for grp in messages:
            if isinstance(grp, Message):
                catalog = self._addMsgToCatalog(grp, catalog)
            elif isinstance(grp, tuple) or isinstance(grp, list):
                for msg in grp:
                    catalog = self._addMsgToCatalog(msg, catalog)
        return catalog

    def _addMsgToCatalog(self, msg, catalog):
        msgId = msg.Singular if not msg.Plural else (msg.Singular,) + msg.Plural
        src = self.sourceService.getById(msg.Source)
        msg.Comments = msg.Comments if msg.Comments else ''
        context = msg.Context if isinstance(msg.Context, str) and msg.Context != '' else None
        catalog.add(id=msgId, locations=((src.Path, msg.LineNumber),), flags=(),
                    auto_comments=(msg.Comments), user_comments=(), context=context)
        return catalog
