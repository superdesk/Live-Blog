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
from ally.container.support import setup
from ally.support.util_io import IInputStream
from babel import localedata, core
from babel.core import Locale, UnknownLocaleError
from babel.messages.catalog import Catalog
from babel.messages.mofile import write_mo
from babel.messages.pofile import read_po, write_po
from collections import Iterable
from copy import copy
from datetime import datetime
from genericpath import isdir, isfile
from internationalization.api.message import IMessageService, Message
from internationalization.api.source import ISourceService, QSource, \
    TYPE_JAVA_SCRIPT
from internationalization.core.spec import IPOFileManager, InvalidLocaleError
from internationalization.support.babel.util_babel import msgId, isMsgTranslated, \
    copyTranslation, fixBabelCatalogAddBug
from io import BytesIO
from os.path import dirname, join
import os

# --------------------------------------------------------------------

# Babel FIX: We need to adjust the dir name for locales since they need to be outside the .egg file
localedata._dirname = localedata._dirname.replace('.egg', '')
core._filename = core._filename.replace('.egg', '')

FORMAT_PO = '%s_%s.po'
# The format of the po files.
FORMAT_MO = '%s_%s.mo'
# The format of the mo files.

# --------------------------------------------------------------------

# TODO: add lock in order to avoid problems when a file is being updated an then read.
@injected
@setup(IPOFileManager)
class POFileManager(IPOFileManager):
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
    
    :param header_comment: the header comment as string, or `None` for the default header
    :param project: the project's name
    :param version: the project's version
    :param copyright_holder: the copyright holder of the catalog
    :param msgid_bugs_address: the email address or URL to submit bug reports to
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
    
    :param width: the maximum line width for the generated output; use `None`, 0, or a negative number to
                  completely disable line wrapping
    :param no_location: do not emit a location comment for every message
    :param omit_header: do not include the ``msgid ""`` entry at the top of the output
    :param sort_output: whether to sort the messages in the output by msgid
    :param sort_by_file: whether to sort the messages in the output by their locations
    :param ignore_obsolete: whether to ignore obsolete messages and not include them in the output; by default
                            they are included as comments
    :param include_previous: include the old msgid as a comment when updating the catalog
    ''')

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
            raise IOError('Unable to access the locale directory %s' % self.locale_dir_path)

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
        catalog = self._build(locale, self.messageService.getMessages(), self._filePath(locale))
        return self._toPOFile(catalog)

    def getGlobalAsDict(self, locale):
        '''
        @see: IPOFileManager.getGlobalAsDict
        '''
        try: locale = Locale.parse(locale)
        except UnknownLocaleError: raise InvalidLocaleError(locale)

        messages = self.messageService.getMessages(qs=QSource(type=TYPE_JAVA_SCRIPT))
        catalog = self._build(locale, messages, self._filePath(locale))
        return self._toDict('', catalog)

    def getComponentPOFile(self, component, locale):
        '''
        @see: IPOFileManager.getComponentPOFile
        '''
        try: locale = Locale.parse(locale)
        except UnknownLocaleError: raise InvalidLocaleError(locale)
        catalog = self._build(locale, self.messageService.getComponentMessages(component),
                              self._filePath(locale, component=component), self._filePath(locale))
        return self._toPOFile(catalog)

    def getComponentAsDict(self, component, locale):
        '''
        @see: IPOFileManager.getComponentAsDict
        '''
        try: locale = Locale.parse(locale)
        except UnknownLocaleError: raise InvalidLocaleError(locale)
        messages = self.messageService.getComponentMessages(component, qs=QSource(type=TYPE_JAVA_SCRIPT))
        catalog = self._build(locale, messages, self._filePath(locale, component=component),
                              self._filePath(locale))
        return self._toDict(component, catalog)

    def getPluginPOFile(self, plugin, locale):
        '''
        @see: IPOFileManager.getPluginPOFile
        '''
        try: locale = Locale.parse(locale)
        except UnknownLocaleError: raise InvalidLocaleError(locale)
        catalog = self._build(locale, self.messageService.getPluginMessages(plugin),
                              self._filePath(locale, plugin=plugin), self._filePath(locale))
        return self._toPOFile(catalog)

    def getPluginAsDict(self, plugin, locale):
        '''
        @see: IPOFileManager.getPluginAsDict
        '''
        try: locale = Locale.parse(locale)
        except UnknownLocaleError: raise InvalidLocaleError(locale)
        messages = self.messageService.getPluginMessages(plugin, qs=QSource(type=TYPE_JAVA_SCRIPT))
        catalog = self._build(locale, messages, self._filePath(locale, plugin=plugin),
                              self._filePath(locale))
        return self._toDict(plugin, catalog)

    def updateGlobalPOFile(self, locale, poFile):
        '''
        @see: IPOFileManager.updateGlobalPOFile
        '''
        try: locale = Locale.parse(locale)
        except UnknownLocaleError: raise InvalidLocaleError(locale)
        assert isinstance(poFile, IInputStream), 'Invalid file object %s' % poFile

        return self._update(locale, self.messageService.getMessages(), poFile, self._filePath(locale),
                            self._filePath(locale, format=FORMAT_MO))

    def updateComponentPOFile(self, component, locale, poFile):
        '''
        @see: IPOFileManager.updateComponentPOFile
        '''
        try: locale = Locale.parse(locale)
        except UnknownLocaleError: raise InvalidLocaleError(locale)
        assert isinstance(poFile, IInputStream), 'Invalid file object %s' % poFile

        return self._update(locale, self.messageService.getComponentMessages(component), poFile,
                            self._filePath(locale, component=component),
                            self._filePath(locale, component=component, format=FORMAT_MO), False)

    def updatePluginPOFile(self, plugin, locale, poFile):
        '''
        @see: IPOFileManager.updatePluginPOFile
        '''
        try: locale = Locale.parse(locale)
        except UnknownLocaleError: raise InvalidLocaleError(locale)
        assert isinstance(poFile, IInputStream), 'Invalid file object %s' % poFile

        return self._update(locale, self.messageService.getPluginMessages(plugin), poFile,
                            self._filePath(locale, plugin=plugin),
                            self._filePath(locale, plugin=plugin, format=FORMAT_MO), False)

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

        for msg in catalog: msg.locations = []

        for msg in messages:
            assert isinstance(msg, Message)
            id = msg.Singular if not msg.Plural else (msg.Singular,) + tuple(msg.Plural)
            src = self.sourceService.getById(msg.Source)
            context = msg.Context if msg.Context != '' else None
            msgC = catalog.get(msg.Singular, context)
            if msgC is None and fallBack is not None:
                assert isinstance(fallBack, Catalog), 'Invalid fall back catalog %s' % fallBack
                msgC = fallBack.get(msg.Singular, context)
                if msgC is not None:
                    msgC.locations = []
                    catalog[msg.Singular] = msgC
            msgCOrig = copy(msgC)
            catalog.add(id, context=msg.Context if msg.Context != '' else None,
                        locations=((src.Path, msg.LineNumber),),
                        user_comments=(msg.Comments if msg.Comments else '',))
            if msgC: fixBabelCatalogAddBug(msgC, catalog.num_plurals)
            if msg.Plural and msgC and msgCOrig and isinstance(msgCOrig.string, str) and msgCOrig.string != '':
                copyTranslation(msgCOrig, msgC)

        creationDate = catalog.creation_date # We need to make sure that the catalog keeps its creation date.
        catalog.creation_date = creationDate
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

    def _toDict(self, domain, catalog):
        '''
        Convert the catalog to a dictionary.
        Format description: @see IPOFileManager.getGlobalAsDict
        
        @param catalog: Catalog
            The catalog to convert to a dictionary.
        @return: dict
            The dictionary in the format specified above.
        '''
        assert isinstance(catalog, Catalog), 'Invalid catalog %s' % catalog

        d = { }
        d[''] = { 'lang' : catalog.locale.language, 'plural-forms' : catalog.plural_forms }
        for msg in catalog:
            if not msg or msg.id == '': continue
            if isinstance(msg.id, (list, tuple)):
                key, key_plural = msg.id
                singular, plural = msg.string[0], msg.string[1]
            else:
                key, key_plural = msg.id, ''
                singular, plural = msg.string, ''
            singular = singular if singular is not None else ''
            plural = plural if plural is not None else ''
            key = key if not msg.context else "%s:%s" % (msg.context, key)
            d[key] = [ key_plural, singular, plural ]
        return { domain : d }

    def _build(self, locale, messages, path, pathGlobal=None):
        '''
        Builds a catalog based on the provided locale paths, the path is used as the main source any messages that are not
        found in path locale but are part of messages will attempt to be extracted from the global path locale.
        
        @param locale: Locale
            The locale.
        @param messages: Iterable(Message)
            The messages to build the PO file on.
        @param path: string
            The path of the targeted PO file from the locale repository.
        @param pathGlobal: string|None
            The path of the global PO file from the locale repository.
        @return: file like object
            File like object that contains the PO file content
        '''
        assert isinstance(locale, Locale), 'Invalid locale %s' % locale
        assert isinstance(messages, Iterable), 'Invalid messages %s' % messages
        assert isinstance(path, str), 'Invalid path %s' % path
        assert pathGlobal is None or isinstance(pathGlobal, str), 'Invalid global path %s' % pathGlobal
        if isfile(path):
            with open(path) as fObj: catalog = read_po(fObj, locale)
        else:
            catalog = Catalog(locale, creation_date=datetime.now(), **self.catalog_config)
        if pathGlobal and isfile(pathGlobal):
            with open(pathGlobal) as fObj: catalogGlobal = read_po(fObj, locale)
        else:
            catalogGlobal = None

        self._processCatalog(catalog, messages, fallBack=catalogGlobal)
        catalog.revision_date = datetime.now()

        return catalog

    def _update(self, locale, messages, poFile, path, pathMO, isGlobal=True):
        assert isinstance(locale, Locale), 'Invalid locale %s' % locale
        assert isinstance(messages, Iterable), 'Invalid messages %s' % messages
        assert isinstance(poFile, IInputStream), 'Invalid file object %s' % poFile
        assert isinstance(path, str), 'Invalid path %s' % path
        assert isinstance(pathMO, str), 'Invalid path MO %s' % pathMO
        assert isinstance(isGlobal, bool), 'Invalid is global flag %s' % isGlobal

        catalog = read_po(poFile, locale=locale)
        assert isinstance(catalog, Catalog), 'Invalid catalog %s' % catalog
        if not catalog:
            # The catalog has no messages, no need for updating.
            return

        if not isGlobal:
            pathGlobal = self._filePath(locale)
            if isfile(pathGlobal):
                with open(pathGlobal) as fObj: catalogGlobal = read_po(fObj, locale)
                self._processCatalog(catalogGlobal, self.messageService.getMessages())
            else:
                isGlobal, path = True, pathGlobal
                messages = self.messageService.getMessages()
        self._processCatalog(catalog, messages)

        if isfile(path):
            with open(path) as fObj: catalogOld = read_po(fObj, locale)
            for msg in catalog:
                msgO = catalogOld.get(msgId(msg), msg.context)
                if not isMsgTranslated(msg) and msgO and isMsgTranslated(msgO):
                    msg.string = msgO.string
            catalog.creation_date = catalogOld.creation_date
        else:
            pathDir = dirname(path)
            if not isdir(pathDir): os.makedirs(pathDir)
            catalog.creation_date = datetime.now()

        if not isGlobal:
            # We remove all the messages that are not translated or have the same translation as in the global locale
            # or are the only plugin that makes use of the message in the global.
            updatedGlobal = False
            for msg in list(catalog):
                id = msgId(msg)
                if not id: continue
                if not isMsgTranslated(msg):
                    catalog.delete(id, msg.context)
                else:
                    msgG = catalogGlobal.get(id, msg.context)
                    if not msgG or msgG.string == msg.string:
                        catalog.delete(id, msg.context)
                    elif not isMsgTranslated(msgG) or msgG.locations == msg.locations:
                        copyTranslation(msg, msgG)
                        catalog.delete(id, msg.context)
                        updatedGlobal = True

            if updatedGlobal:
                # We remove all the messages that are not translated.
                for msg in list(catalogGlobal):
                    if not isMsgTranslated(msg):
                        catalogGlobal.delete(msgId(msg), msg.context)

                catalogGlobal.revision_date = datetime.now()
                with open(pathGlobal, 'wb') as fObj: write_po(fObj, catalogGlobal, **self.write_po_config)
                with open(self._filePath(locale, format=FORMAT_MO), 'wb') as fObj: write_mo(fObj, catalogGlobal)
        else:
            # We remove all the messages that are not translated.
            for msg in list(catalog):
                if not isMsgTranslated(msg):
                    catalog.delete(msgId(msg), msg.context)

        catalog.revision_date = datetime.now()
        with open(path, 'wb') as fObj: write_po(fObj, catalog, **self.write_po_config)
        with open(pathMO, 'wb') as fObj: write_mo(fObj, catalog)
