'''
Created on Mar 13, 2012

@package: internationalization
@copyright: 2012 Sourcefabric o.p.s.
@license: http://www.gnu.org/licenses/gpl-3.0.txt
@author: Mugur Rus

Implementation for the PO file management.
'''

from babel.messages.catalog import Catalog
from internationalization.api.message import IMessageService
from ally.container import wire
from ally.container.ioc import injected
from internationalization.api.POFileManager import IPOFileManager
from genericpath import isdir, isfile
import os
from internationalization.api.source import ISourceService, QSource
from introspection.api.component import Component
from introspection.api.plugin import Plugin
from ally.api.type import Iter
from internationalization.api.message import Message
from babel.messages.pofile import read_po, write_po
from os.path import join

# --------------------------------------------------------------------

@injected
class POFileManagerAlchemy(IPOFileManager):
    '''
    Implementation for @see: IPOFileManager
    '''

    messageService = IMessageService; wire.entity('messageService')

    sourceService = ISourceService; wire.entity('sourceService')

    localeDirPath = str

    _cacheDir = '_cache'

    _internalDir = '_internal'

    def __init__(self):
        assert isinstance(self.messageService, IMessageService), 'Invalid message service %s' % self.messageService
        assert isinstance(self.sourceService, ISourceService), 'Invalid source file service %s' % self.sourceService
        assert isinstance(self.localeDirPath, str), 'Invalid locale directory %s' % self.localeDirPath
        if not isdir(self.localeDirPath) or not os.access(self.repositoryPath, os.W_OK):
            raise Exception('Unable to access the repository directory %s' % self.localeDirPath)

    def getGlobalPOFile(self, locale):
        '''
        @see: IPOFileManager.getGlobalPOFile
        '''
        poFilePath = self._cachedPOFilePath(locale)
        if self._isSyncPOFile(locale):
            return poFilePath
        keys = self.messageService.getMessages()
        with poFilePath as fileObj:
            return self._buildPOFile(fileObj, locale, keys)
        return poFilePath

    def getComponentPOFile(self, component, locale):
        '''
        @see: IPOFileManager.getComponentPOFile
        '''
        poFilePath = self._cachedPOFilePath(locale, component)
        if self._isSyncPOFile(locale, component):
            return poFilePath
        keys = self.messageService.getComponentMessages(component)
        exceptionsCatalog = self._readPOFile(self._internalPOFilePath(locale, component), locale)
        with poFilePath as fileObj:
            self._buildPOFile(fileObj, locale, keys, exceptionsCatalog)
        return poFilePath

    def getPluginPOFile(self, plugin, locale):
        '''
        @see: IPOFileManager.getPluginPOFile
        '''
        poFilePath = self._cachedPOFilePath(locale, plugin=plugin)
        if self._isSyncPOFile(locale, plugin=plugin):
            return poFilePath
        keys = self.messageService.getPluginMessages(plugin)
        exceptionsCatalog = self._readPOFile(self._internalPOFilePath(locale, plugin=plugin), locale)
        with poFilePath as fileObj:
            self._buildPOFile(fileObj, locale, keys, exceptionsCatalog)
        return poFilePath

    def updateGlobalPOFile(self, locale):
        '''
        @see: IPOFileManager.updateGlobalPOFile
        '''

    def updateComponentPOFile(self, component, locale):
        '''
        @see: IPOFileManager.updateComponentPOFile
        '''

    def updatePluginPOFile(self, plugin, locale):
        '''
        @see: IPOFileManager.updatePluginPOFile
        '''

    def _buildPOFile(self, fileObj, locale:str=None, keys:Iter(Message)=Iter(Message),
                     exceptionsCat:Catalog=Catalog()):
        globalCatalog = self._readPOFile(self._internalPOFilePath(locale), locale)
        for msg in exceptionsCat:
            globalCatalog.add(msg.id, msg.string, msg.locations, msg.flags, msg.auto_comments,
                              msg.user_comments, msg.previous_id, msg.lineno, msg.context)
        templateCatalog = self._buildCatalog(keys, locale)
        globalCatalog.update(templateCatalog)
        write_po(fileObj)

    def _readPOFile(self, path, locale:str=None) -> Catalog:
        if not isfile(path):
            return Catalog()
        with path as fObj:
            return read_po(fObj, locale)

    def _poFileName(self, locale:str=None, component:Component.Id=None, plugin:Plugin.Id=None):
        fileLocale = '_' + locale if locale else ''
        if component:
            return 'component_' + component + fileLocale + '.po'
        elif plugin:
            return 'plugins' + plugin + fileLocale + '.po'
        else:
            return 'global' + fileLocale + '.po'

    def _internalPOFilePath(self, locale:str=None, component:Component.Id=None, plugin:Plugin.Id=None):
        return join(self.localeDirPath, self._internalDir, self._poFileName(locale, component, plugin))

    def _cachedPOFilePath(self, locale:str=None, component:Component.Id=None, plugin:Plugin.Id=None):
        return join(self.localeDirPath, self._cacheDir, self._poFileName(locale, component, plugin))

    def _isSyncPOFile(self, locale:str=None, component:Component.Id=None, plugin:Plugin.Id=None):
        path = self._cachedPOFilePath(locale, component, plugin)
        if not isfile(path):
            return False
        fileMTime = os.stat(path).st_mtime
        return fileMTime >= self._messagesLastModified(component, plugin)

    def _messagesLastModified(self, component:Component.Id=None, plugin:Plugin.Id=None):
        q = QSource()
        q.lastModified.orderDesc()
        if component:
            q.component = component
        if plugin:
            q.plugin = plugin
        sources = self.sourceService.getAll(0, 1, q)
        if sources:
            return sources[0].LastModified
        return None

    def _buildCatalog(self, messages, locale:str=None):
        catalog = Catalog(locale)
        if isinstance(messages, Iter(Message)):
            messages = (messages,)
        for grp in messages:
            for msg in grp:
                msgId = msg.Singular if not msg.Plural else (msg.Singular,) + msg.Plural
                catalog.add(id=msgId, locations=((msg.Source.Path, msg.LineNumber),), flags=(),
                            auto_comments=(msg.Comments), user_comments=(), context=msg.Context)
        return catalog
