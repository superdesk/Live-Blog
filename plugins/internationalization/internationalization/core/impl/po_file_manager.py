'''
Created on Mar 13, 2012

@package: internationalization
@copyright: 2012 Sourcefabric o.p.s.
@license: http://www.gnu.org/licenses/gpl-3.0.txt
@author: Mugur Rus

Implementation for the PO file management.
'''

from ally.container import wire
from ally.container.ioc import injected
from babel import localedata, core
from babel.messages.catalog import Catalog
from babel.messages.mofile import write_mo
from babel.messages.pofile import read_po, write_po
from babel.util import odict
from cdm.spec import PathNotFound
from datetime import datetime
from genericpath import isdir, isfile
from internationalization.api.message import IMessageService, Message
from internationalization.api.source import ISourceService, QSource
from internationalization.core.spec import IPOFileManager, InvalidLocaleError
from introspection.api.component import Component
from introspection.api.plugin import Plugin
from io import BytesIO
from os.path import dirname, join
import os
from collections import Iterable
from babel.core import Locale, UnknownLocaleError


# --------------------------------------------------------------------

# Babel FIX: We need to adjust the dir name for locales since they need to be outside the .egg file
localedata._dirname = localedata._dirname.replace('.egg', '')
core._filename = core._filename.replace('.egg', '')

FORMAT_PO = '%s_%s.po'
# The format of the po files.
FORMAT_MO = '%s_%s.mo'
# The format of the mo files.

# --------------------------------------------------------------------

@injected
class POFileManagerDB(IPOFileManager):
    '''
    Implementation for @see: IPOFileManager
    '''

    locale_dir_path = join('workspace', 'locale'); wire.config('locale_dir_path', doc='''
    The locale repository path''')
    catalog_config = {
                      'header_comment':'''\
# Translations template for PROJECT.
# Copyright (C) YEAR ORGANIZATION
# This file is distributed under the same license as the PROJECT project.
# Gabriel Nistor <gabriel.nistor@sourcefabric.org>, YEAR.
#''',
                      'project': 'Sourcefabric',
                      'version': '1.0',
                      'copyright_holder': 'Sourcefabric o.p.s.',
                      'msgid_bugs_address': 'contact@sourcefabric.org',
                      'last_translator': 'Automatic',
                      'language_team': 'Automatic',
                      'fuzzy': False,
                      }; wire.config('catalog_config', doc='''
    The global catalog default configuration for templates.
    
    :param header_comment: the header comment as string, or `None` for the
                               default header
    :param project: the project's name
    :param version: the project's version
    :param copyright_holder: the copyright holder of the catalog
    :param msgid_bugs_address: the email address or URL to submit bug
                               reports to
    :param creation_date: the date the catalog was created
    :param revision_date: the date the catalog was revised
    :param last_translator: the name and email of the last translator
    :param language_team: the name and email of the language team
    :param charset: the encoding to use in the output
    :param fuzzy: the fuzzy bit on the catalog header
    ''')
    write_po_config = {
                       'no_location': False,
                       'omit_header': False,
                       'sort_output': True,
                       'sort_by_file': True,
                       'ignore_obsolete': True,
                       'include_previous': False,
                       }; wire.config('write_po_config', doc='''
    The configurations used when writing the PO files.
    
    :param width: the maximum line width for the generated output; use `None`,
                  0, or a negative number to completely disable line wrapping
    :param no_location: do not emit a location comment for every message
    :param omit_header: do not include the ``msgid ""`` entry at the top of the
                        output
    :param sort_output: whether to sort the messages in the output by msgid
    :param sort_by_file: whether to sort the messages in the output by their
                         locations
    :param ignore_obsolete: whether to ignore obsolete messages and not include
                            them in the output; by default they are included as
                            comments
    :param include_previous: include the old msgid as a comment when
                             updating the catalog''')

    messageService = IMessageService; wire.entity('messageService')
    sourceService = ISourceService; wire.entity('sourceService')

    def __init__(self):
        assert isinstance(self.locale_dir_path, str), 'Invalid locale directory %s' % self.locale_dir_path
        assert isinstance(self.catalog_config, dict), 'Invalid catalog configurations %s' % self.catalog_config
        assert isinstance(self.write_po_config, dict), 'Invalid write PO configurations %s' % self.write_po_config
        assert isinstance(self.messageService, IMessageService), 'Invalid message service %s' % self.messageService
        assert isinstance(self.sourceService, ISourceService), 'Invalid source file service %s' % self.sourceService

        if not os.path.exists(self.locale_dir_path): os.makedirs(self.locale_dir_path)
        if not isdir(self.locale_dir_path) or not os.access(self.locale_dir_path, os.W_OK):
            raise Exception('Unable to access the repository directory %s' % self.locale_dir_path)

    def getGlobalPOTimestamp(self, locale):
        '''
        @see: IPOFileManager.getGlobalPOTimestamp
        '''
        try: locale = Locale.parse(locale)
        except UnknownLocaleError: raise InvalidLocaleError(locale)
        return self._lastModified(locale)

    def getComponentPOTimestamp(self, component, locale):
        '''
        @see: IPOFileManager.getComponentPOTimestamp
        '''
        assert isinstance(component, str), 'Invalid component id %s' % component
        try: locale = Locale.parse(locale)
        except UnknownLocaleError: raise InvalidLocaleError(locale)
        return self._lastModified(locale, component=component)

    def getPluginPOTimestamp(self, plugin, locale):
        '''
        @see: IPOFileManager.getComponentPOTimestamp
        '''
        assert isinstance(plugin, str), 'Invalid plugin id %s' % plugin
        try: locale = Locale.parse(locale)
        except UnknownLocaleError: raise InvalidLocaleError(locale)

        return self._lastModified(locale, plugin=plugin)

    # --------------------------------------------------------------------

    def getGlobalPOFile(self, locale):
        '''
        @see: IPOFileManager.getGlobalPOFile
        '''
        try: locale = Locale.parse(locale)
        except UnknownLocaleError: raise InvalidLocaleError(locale)
        path = self._filePath(locale)
        if isfile(path):
            with open(path) as fObj: catalog = read_po(fObj, locale)
        else:
            catalog = Catalog(locale, **self.catalog_config)

        self._processCatalog(catalog, self.messageService.getMessages())

        return self._toPOFile(catalog)

    def getComponentPOFile(self, component, locale):
        '''
        @see: IPOFileManager.getComponentPOFile
        '''
        try: locale = Locale.parse(locale)
        except UnknownLocaleError: raise InvalidLocaleError(locale)
        messages = self.messageService.getComponentMessages(component)
        pathGlobal, path = self._filePath(locale), self._filePath(locale, component=component)
        if isfile(path):
            with open(path) as fObj: catalog = read_po(fObj, locale)
        else:
            catalog = Catalog(locale, **self.catalog_config)
        if isfile(pathGlobal):
            with open(pathGlobal) as fObj: catalogGlobal = read_po(fObj, locale)
        else:
            catalogGlobal = None

        self._processCatalog(catalog, messages, fallBack=catalogGlobal)

        return self._toPOFile(catalog)

    def getPluginPOFile(self, plugin, locale):
        '''
        @see: IPOFileManager.getPluginPOFile
        '''
        try: locale = Locale.parse(locale)
        except UnknownLocaleError: raise InvalidLocaleError(locale)

        messages = self.messageService.getPluginMessages(plugin)
        pathGlobal, path = self._filePath(locale), self._filePath(locale, plugin=plugin)
        if isfile(path):
            with open(path) as fObj: catalog = read_po(fObj, locale)
        else:
            catalog = Catalog(locale, **self.catalog_config)
        if isfile(pathGlobal):
            with open(pathGlobal) as fObj: catalogGlobal = read_po(fObj, locale)
        else:
            catalogGlobal = None

        self._processCatalog(catalog, messages, fallBack=catalogGlobal)

        return self._toPOFile(catalog)

    def updateGlobalPOFile(self, locale, poFile):
        '''
        @see: IPOFileManager.updateGlobalPOFile
        '''
        assert hasattr(poFile, 'read'), 'Invalid file object %s' % poFile
        try: locale = Locale.parse(locale)
        except UnknownLocaleError: raise InvalidLocaleError(locale)
        update = read_po(poFile)
        assert isinstance(update, Catalog), 'Invalid catalog %s' % update

        path = self._filePath(locale)
        if isfile(path):
            with open(path) as fObj: catalog = read_po(fObj, locale)
            pathDir = dirname(path)
            if not isdir(pathDir): os.makedirs(pathDir)
        else:
            catalog = Catalog(locale, **self.catalog_config)
        self._processCatalog(catalog, self.messageService.getMessages())

        for msg in update:
            msgC = catalog.get(msg.id, msg.context)
            if msgC: msgC.string = msg.string

        with open(path, 'wb') as fObj: write_po(fObj, catalog, **self.write_po_config)
        with open(self._filePath(locale, format=FORMAT_MO), 'wb') as fObj: write_mo(fObj, catalog)

    def updateComponentPOFile(self, component, locale, poFile):
        '''
        @see: IPOFileManager.updateComponentPOFile
        '''
        assert hasattr(poFile, 'read'), 'Invalid file object %s' % poFile
        assert isinstance(locale, str), 'Invalid locale %s' % locale
        self._processPOFile(component, None, locale, read_po(poFile))

    def updatePluginPOFile(self, plugin, locale, poFile):
        '''
        @see: IPOFileManager.updatePluginPOFile
        '''
        assert hasattr(poFile, 'read'), 'Invalid file object %s' % poFile
        assert isinstance(locale, str), 'Invalid locale %s' % locale
        self._processPOFile(None, plugin, locale, read_po(poFile))

    # --------------------------------------------------------------------

    def _filePath(self, locale, component=None, plugin=None, format=FORMAT_PO):
        '''
        Returns the path to the internal PO file corresponding to the given locale and / or
        component / plugin. If no component of plugin was specified it returns the
        name of the global PO file.
        
        @param locale: Locale
            The locale.
        @param component: string
            The component id.
        @param plugin: string
            The plugin id.
        @param format: string
            The format pattern for the file, the default is the PO file.
        @return: string
            The file path.
        '''
        assert isinstance(locale, Locale), 'Invalid locale %s' % locale
        assert component is None or isinstance(component, str), 'Invalid component %s' % component
        assert plugin is None or isinstance(plugin, str), 'Invalid plugin %s' % plugin
        assert not(component and plugin), 'Cannot process a component id %s and a plugin id %s' % (component, plugin)

        path = [self.locale_dir_path]
        if component:
            path.append('component')
            name = component
        elif plugin:
            path.append('plugin')
            name = plugin
        else:
            name = 'global'

        path.append(format % (name, locale))

        return join(*path)

    def _lastModified(self, locale, component=None, plugin=None):
        '''
        Provides the last modification time stamp for the provided locale. You can specify the component id in order to
        get the last modification for the component domain, or plugin or either to get the global domain modification.
        
        @param locale: Locale
            The locale to get the last modification for.
        @param component: string|None
            The component id to get the last modification for.
        @param plugin: string|None
            The plugin id to get the last modification for.
        @return: datetime|None
            The last modification time stamp, None if there is no such time stamp available.
        '''
        assert isinstance(locale, Locale), 'Invalid locale %s' % locale
        assert not(component and plugin), 'Cannot process a component id %s and a plugin id %s' % (component, plugin)

        q = QSource()
        q.lastModified.orderDesc()
        if component: q.component = component
        elif plugin: q.plugin = plugin
        sources = self.sourceService.getAll(0, 1, q)
        try: lastModified = next(iter(sources)).LastModified
        except StopIteration: lastModified = None

        path = self._filePath(locale, component, plugin)
        if isfile(path):
            lastModified = max(lastModified, datetime.fromtimestamp(os.stat(path).st_mtime))
        return lastModified

    def _processCatalog(self, catalog, messages, fallBack=None):
        '''
        Processes a catalog based on the given messages list. Basically the catalog will be made in sync with the list of
        messages.
        
        @param catalog: Catalog
            The catalog to keep in sync.
        @param messages: Iterable
            The messages to update the catalog with.
        @param fallBack: Catalog
            The fall back catalog to get the missing catalog messages .
        @return: Catalog
            The same catalog
        '''
        assert isinstance(catalog, Catalog), 'Invalid catalog %s' % catalog
        assert isinstance(messages, Iterable), 'Invalid messages list %s' % messages

        template = Catalog()
        for msg in messages:
            assert isinstance(msg, Message)
            id = msg.Singular if not msg.Plural else (msg.Singular,) + tuple(msg.Plural)
            src = self.sourceService.getById(msg.Source)
            msgT = template.add(id, context=msg.Context, locations=((src.Path, msg.LineNumber),),
                                user_comments=(msg.Comments if msg.Comments else '',))
            msgC = catalog.get(msgT.id, msgT.context)
            if msgC is None and fallBack is not None:
                assert isinstance(fallBack, Catalog), 'Invalid fall back catalog %s' % fallBack
                msgC = fallBack.get(msgT.id, msgT.context)
                if msgC is not None: catalog[msgT.id] = msg

        catalog.update(template)
        return catalog

    def _toPOFile(self, catalog):
        '''
        Convert the catalog to a PO file like object.
        
        @param catalog: Catalog
            The catalog to convert to a file.
        @return: file read object
            A file like object to read the PO file from.
        '''
        assert isinstance(catalog, Catalog), 'Invalid catalog %s' % catalog

        fileObj = BytesIO()
        write_po(fileObj, catalog, **self.write_po_config)
        fileObj.seek(0)
        return fileObj






















    def _buildPOFile(self, locale, template=None, exceptions=None):
        '''
        Builds a PO file from the given file (as file object) to read from, for the
        given locale, using the given template and exceptions catalogs.
        Messages not in the template will be discarded while messages from the
        exceptions catalog will overwrite the messages with the same keys that
        existed in the given PO file.
        
        @param locale: Locale
            The locale code
        @param template: Catalog
            The template catalog used to filter the messages. Only keys from this
            template will be kept in the catalog.
        @param exceptions: Catalog
            Messages that override the generic translations.
        @return: file like object
            File like object that contains the PO file content
        '''
        assert isinstance(locale, Locale), 'Invalid locale %s' % locale
        if not exceptions: exceptions = Catalog(locale)

        assert isinstance(exceptions, Catalog), 'Invalid exceptions catalog %s' % exceptions

        try:
            globalCatalog = self._readPOFile(self._filePath(locale)['po'], locale)
        except PathNotFound:
            globalCatalog = Catalog(locale)
        for msg in globalCatalog:
            if not msg or msg.id == '': continue
            exceptions[msg.id] = msg

        if template:
            assert isinstance(template, Catalog), 'Invalid template catalog %s' % template
            exceptions.update(template)

        exceptions.obsolete = odict()
        fileObj = BytesIO()
        write_po(fileObj, exceptions)
        fileObj.seek(0)
        return fileObj

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

