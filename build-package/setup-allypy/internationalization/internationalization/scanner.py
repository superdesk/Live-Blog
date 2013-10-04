'''
Created on Mar 5, 2012

@package: internationalization
@copyright: 2011 Sourcefabric o.p.s.
@license: http://www.gnu.org/licenses/gpl-3.0.txt
@author: Nistor Gabriel

The scanner used for extracting the localized text messages.
'''

from admin.introspection.api.component import IComponentService, Component
from admin.introspection.api.plugin import IPluginService, Plugin
from ally.container import wire, app
from ally.container.ioc import injected
from ally.container.support import setup
from babel.messages.extract import extract_nothing, extract_python, \
    _strip_comment_tags, empty_msgid_warning, extract_javascript
from internationalization.core.impl.extract_html import extract_html
from babel.util import pathmatch
from datetime import datetime
from functools import partial
from internationalization.api.file import IFileService, QFile, File
from internationalization.api.message import IMessageService, Message
from internationalization.api.source import ISourceService, TYPES, Source, \
    QSource
from io import BytesIO, TextIOWrapper
from os import path
from zipfile import ZipFile
import logging
import os

# --------------------------------------------------------------------

log = logging.getLogger(__name__)

# --------------------------------------------------------------------

METHOD_MAP = [('**.py', 'python'), ('**.js', 'javascript'), ('**.html', 'html'), ('**.dust', 'html')]
# A list of ``(pattern, method)`` tuples that maps of extraction method names to extended global patterns
METHOD_EXTRACTOR = {'ignore': extract_nothing, 'python': extract_python, 'javascript': extract_javascript, 'html': extract_html}
# The modethod extractors to be used.

KEYWORDS = {
            'gettext': None,
            '_': None,
            'ngettext': (1, 2),
            'pgettext': (1, 2),
            'C_': (1, 2),
            'npgettext': (1, 2, 3),
            'N_': None,
            'NC_': (1, 2),
            }
# A dictionary mapping keywords (i.e. names of functions that should be recognized as translation functions) to tuples
# that specify which of their arguments contain localizable strings

COMMENT_TAGS = ('NOTE')
# A list of tags of translator comments to search for and include in the results

# --------------------------------------------------------------------

@injected
@setup(name='scanner')
class Scanner:
    '''
    The class that provides the scanner.
    '''

    componentService = IComponentService; wire.entity('componentService')
    pluginService = IPluginService; wire.entity('pluginService')
    fileService = IFileService; wire.entity('fileService')
    sourceService = ISourceService; wire.entity('sourceService')
    messageService = IMessageService; wire.entity('messageService')

    def __init__(self):
        '''
        Construct the scanner.
        '''
        assert isinstance(self.componentService, IComponentService), \
        'Invalid component service %s' % self.componentService
        assert isinstance(self.pluginService, IPluginService), 'Invalid plugin service %s' % self.pluginService
        assert isinstance(self.fileService, IFileService), 'Invalid file service %s' % self.fileService
        assert isinstance(self.sourceService, ISourceService), 'Invalid source service %s' % self.sourceService
        assert isinstance(self.messageService, IMessageService), 'Invalid message service %s' % self.messageService
    
    @app.populate(app.CHANGED)
    def scanLocalization(self):
        '''
        Scans the application for localization messages.
        '''
#        log.info('Scanning the application distribution for localized messages')
#        self.scanComponents()
#        self.scanPlugins()
        
    # ----------------------------------------------------------------

    def scanComponents(self):
        '''
        Scan the current application components for the localized text messages.
        '''
        for component in self.componentService.getComponents():
            assert isinstance(component, Component)
            files = {file.Path: file for file in self.fileService.getAll(q=QFile(component=component.Id))}
            if component.InEgg:
                lastModified = modificationTimeFor(component.Path)
                file = files.get(component.Path)
                if file and lastModified <= file.LastModified:
                    log.info('No modifications for component zip file "%s" in %s', component.Path, component.Name)
                    continue
                if not file:
                    file = File()
                    file.Component = component.Id
                    file.Path = component.Path
                    file.LastModified = lastModified
                    files[component.Path] = file
                    self.fileService.insert(file)
                else:
                    file.LastModified = lastModified
                    self.fileService.update(file)
                scanner = scanZip(component.Path)
            else:
                lastModified, scanner = None, scanFolder(component.Path)

            files.update({source.Path: source for source in self.sourceService.getAll(q=QSource(component=component.Id))})
            self._persist(files, scanner, component.Path, lastModified, component.Id, None)

    def scanPlugins(self):
        '''
        Scan the current application plugins for the localized text messages.
        '''
        for plugin in self.pluginService.getPlugins():
            assert isinstance(plugin, Plugin)
            files = {file.Path: file for file in self.fileService.getAll(q=QFile(plugin=plugin.Id))}
            if plugin.InEgg:
                lastModified = modificationTimeFor(plugin.Path)
                file = files.get(plugin.Path)
                if file and lastModified <= file.LastModified:
                    log.info('No modifications for plugin zip file "%s" in %s', plugin.Path, plugin.Name)
                    continue
                if not file:
                    file = File()
                    file.Plugin = plugin.Id
                    file.Path = plugin.Path
                    file.LastModified = lastModified
                    files[plugin.Path] = file
                    self.fileService.insert(file)
                else:
                    file.LastModified = lastModified
                    self.fileService.update(file)
                scanner = scanZip(plugin.Path)
            else:
                lastModified, scanner = None, scanFolder(plugin.Path)


            files.update({source.Path: source for source in self.sourceService.getAll(q=QSource(plugin=plugin.Id))})
            self._persist(files, scanner, plugin.Path, lastModified, None, plugin.Id)

    # ----------------------------------------------------------------

    def _persist(self, files, scanner, path, lastModified, componentId, pluginId):
        '''
        Persist the sources and messages. 
        '''
        assert isinstance(files, dict), 'Invalid files %s' % files
        processModified = lastModified is None
        for filePath, method, extractor in scanner:
            assert method in TYPES, 'Invalid method %s' % method

            file = files.get(filePath)
            if processModified:
                lastModified = modificationTimeFor(filePath)
                if file:
                    assert isinstance(file, File)
                    if lastModified <= file.LastModified:
                        log.info('No modifications for file "%s"', filePath)
                        continue
                    file.LastModified = lastModified
                    self.fileService.update(file)

            if isinstance(file, Source): source = file
            else: source = None
            messages = None
            try:
                for text, context, lineno, comments in extractor:
                    if not source:
                        if file: self.fileService.delete(file.Id)
                        source = Source()
                        source.Component = componentId
                        source.Plugin = pluginId
                        source.Path = filePath
                        source.Type = method
                        source.LastModified = lastModified
                        files[filePath] = source
                        self.sourceService.insert(source)

                    if messages is None: messages = {msg.Singular:msg for msg in self.messageService.getMessages(source.Id)}

                    if isinstance(text, str): singular, plurals = text, None
                    elif len(text) == 1: singular, plurals = text[0], None
                    else: singular, plurals = text[0], list(text[1:])

                    msg = messages.get(singular)
                    if not msg:
                        msg = Message()
                        msg.Source = source.Id
                        msg.Singular = singular
                        msg.Plural = plurals
                        msg.Context = context
                        msg.LineNumber = lineno
                        msg.Comments = '\n'.join(comments)

                        self.messageService.insert(msg)
                        messages[singular] = msg
                    else:
                        msg.Plural = plurals
                        msg.Context = context
                        msg.LineNumber = lineno
                        msg.Comments = '\n'.join(comments)
                        self.messageService.update(msg)
            except UnicodeDecodeError as e:
                log.error('%s: %s' % (filePath, str(e)))

            if processModified and filePath not in files:
                file = File()
                file.Component = componentId
                file.Plugin = pluginId
                file.Path = filePath
                file.LastModified = lastModified
                files[filePath] = file
                self.fileService.insert(file)

# --------------------------------------------------------------------

modificationTimeFor = lambda path: datetime.fromtimestamp(os.stat(path).st_mtime).replace(microsecond=0)
# Provides the last update time for the provided full path.

def scanZip(zipFilePath):
    '''
    Scan a zip that is found on the provided path.
    
    @param zipFilePath: string
        The zip path.
    @return: tuple(string, string, generator)
        Returns a tuple containing: (filePath, method, generator(@see: process))
    '''
    zipFile = ZipFile(zipFilePath)
    names = zipFile.namelist()
    names.sort()
    for name in names:
        for pattern, method in METHOD_MAP:
            if pathmatch(pattern, name):
                filePath = zipFilePath + '/' + name
                def openZip():
                    with zipFile.open(name, 'r') as f:
                        return BytesIO(f.read())
                yield filePath, method, process(openZip, method)

def scanFolder(folderPath):
    '''
    Scan a folder that is found on the provided path.
    
    @param folderPath: string
        The folder path.
    @return: tuple(string, string, generator)
        Returns a tuple containing: (filePath, method, generator(@see: process))
    '''
    assert isinstance(folderPath, str), 'Invalid folder path %s' % folderPath
    for root, _dirnames, filenames in os.walk(folderPath):
        filenames.sort()
        for name in filenames:
            name = path.relpath(os.path.join(root, name)).replace(os.sep, '/')
            for pattern, method in METHOD_MAP:
                if pathmatch(pattern, name):
                    filePath = name.replace('/', os.sep)
                    yield filePath, method, process(partial(open, name, 'rb'), method)

def process(openFile, method):
    '''
    Process the content of the file generated by the openFile.
    
    @param openFile: callable
        The open file function.
    @param method: string
        The method used for processing the file.
    @param message: string|list[string]|tuple(string)
        The message to be processed.
    @return: tuple(string|tuple(string), string, integer, string)
        Returns a tuple containing: (message, context, lineno, comments)
    '''
    assert callable(openFile), 'Invalid open file function %s' % openFile
    assert isinstance(method, str), 'Invalid method %s' % method

    with openFile() as fileObj:
        for fname, lineno, message, comments in extract(method, TextIOWrapper(fileObj, encoding='UTF-8')):
            if fname in ('pgettext', 'C_', 'NC_'): cntxt, message = message
            elif fname == 'npgettext': cntxt, *message = message
            else: cntxt = None

            assert log.debug('%s (%s) #%s' % (message, cntxt, comments)) or True
            yield message, cntxt, lineno, comments

# --------------------------------------------------------------------

def extract(method, fileobj, keywords=KEYWORDS, comment_tags=COMMENT_TAGS, options=None, strip_comment_tags=False):
    '''
    Extracted from @see: babel.messages.extract in order to get also the function name and additional messages.
    Extract messages from the given file-like object using the specified
    extraction method.

    This function returns a list of tuples of the form:

        ``(funcname, lineno, messages, comments)``

    @see: babel.messages.extract.extract
    '''
    func = None
    if ':' in method or '.' in method:
        if ':' not in method:
            lastdot = method.rfind('.')
            module, attrname = method[:lastdot], method[lastdot + 1:]
        else:
            module, attrname = method.split(':', 1)
        func = getattr(__import__(module, {}, {}, [attrname]), attrname)
    else:
        func = METHOD_EXTRACTOR.get(method)
    if func is None:
        raise ValueError('Unknown extraction method %r' % method)

    results = func(fileobj, list(keywords.keys()), comment_tags, options=options or {})

    for lineno, funcname, messages, comments in results:
        if funcname:
            spec = keywords[funcname] or (1,)
        else:
            spec = (1,)
        if not isinstance(messages, (list, tuple)): messages = [messages]

        if not messages: continue

        # Validate the messages against the keyword's specification
        msgs = []
        invalid = False
        # last_index is 1 based like the keyword spec
        last_index = len(messages)
        for index in spec:
            if last_index < index:
                # Not enough arguments
                invalid = True
                break
            message = messages[index - 1]
            if message is None:
                invalid = True
                break
            msgs.append(message)
        if invalid:
            continue

        first_msg_index = spec[0] - 1
        if not messages[first_msg_index]:
            # An empty string msgid isn't valid, emit a warning
            where = '%s:%i' % (hasattr(fileobj, 'name') and fileobj.name or '(unknown)', lineno)
            log.error(empty_msgid_warning % where)
            continue

        messages = tuple(msgs)
        if len(messages) == 1: messages = messages[0]

        if strip_comment_tags: _strip_comment_tags(comments, comment_tags)

        yield funcname, lineno, messages, comments
