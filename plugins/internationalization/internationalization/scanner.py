'''
Created on Mar 5, 2012

@package: internationalization
@copyright: 2011 Sourcefabric o.p.s.
@license: http://www.gnu.org/licenses/gpl-3.0.txt
@author: Nistor Gabriel

The scanner used for extracting the localized text messages.
'''

from ally.container import wire
from ally.container.ioc import injected
from ally.internationalization import textdomain
from babel.messages.extract import extract_nothing, extract_python, GROUP_NAME, \
    _strip_comment_tags, empty_msgid_warning
from babel.util import pathmatch
from datetime import datetime
from functools import partial
from internationalization.api.message import IMessageService, Message
from internationalization.api.source import ISourceService, QSource, TYPES, \
    Source
from introspection.api.component import IComponentService, Component
from introspection.api.plugin import IPluginService, Plugin
from io import BytesIO
from os import path
from zipfile import ZipFile
import logging
import os

# --------------------------------------------------------------------

log = logging.getLogger(__name__)

# --------------------------------------------------------------------

METHOD_MAP = [('**.py', 'python')]#, ('**.js', 'javascript'), ('**.html', 'javascript')]
# A list of ``(pattern, method)`` tuples that maps of extraction method names to extended global patterns

DOMAIN_DEFAULT = textdomain()
# The default domain used.
LOCALE_DEFAULT = 'en'
# The default locale.

KEYWORDS = {
            'textlocale': None,
            'gettext': None,
            '_': None,
            'textdomain': None,
            'dgettext': (1, 2),
            'ngettext': (1, 2),
            'dngettext': (1, 2, 3),
            'pgettext': (1, 2),
            'C_': (1, 2),
            'dpgettext': (1, 2, 3),
            'npgettext': (1, 2, 3),
            'dnpgettext': (1, 2, 3, 4),
            'N_': None,
            'NC_': (1, 2),
            }
# A dictionary mapping keywords (i.e. names of functions that should be recognized as translation functions) to tuples
# that specify which of their arguments contain localizable strings

COMMENT_TAGS = ('NOTE')
# A list of tags of translator comments to search for and include in the results

# --------------------------------------------------------------------

@injected
class Scanner:
    '''
    The class that provides the scanner.
    '''
    
    componentService = IComponentService; wire.entity('componentService')
    pluginService = IPluginService; wire.entity('pluginService')
    sourceService = ISourceService; wire.entity('sourceService')
    messageService = IMessageService; wire.entity('messageService')
    
    def __init__(self):
        '''
        Construct the scanner.
        '''
        assert isinstance(self.componentService, IComponentService), \
        'Invalid component service %s' % self.componentService
        assert isinstance(self.pluginService, IPluginService), 'Invalid plugin service %s' % self.pluginService
        assert isinstance(self.sourceService, ISourceService), 'Invalid source service %s' % self.sourceService
        assert isinstance(self.messageService, IMessageService), 'Invalid message service %s' % self.messageService

    def scanComponents(self):
        '''
        Scan the current application components for the localized text messages.
        '''
        for component in self.componentService.getComponents():
            assert isinstance(component, Component)
            sources = {source.Path:source for source in self.sourceService.getAll(q=QSource(component=component.Id))}
            if component.InEgg:
                lastModified = modificationTimeFor(component.Path)
                if sources and all(lastModified <= source.LastModified for source in sources.values()):
                    log.info('No modifications for zip file "%s" in %s', component.Path, component.Name)
                    continue
                scanner = scanZip(component.Path)
            else:
                lastModified, scanner = None, scanFolder(component.Path)
            
            self._persist(sources, scanner, component.Path, lastModified, component.Id, None)
            
    def scanPlugins(self):
        '''
        Scan the current application plugins for the localized text messages.
        '''
        for plugin in self.pluginService.getPlugins():
            assert isinstance(plugin, Plugin)
            sources = {source.Path:source for source in self.sourceService.getAll(q=QSource(plugin=plugin.Id))}
            if plugin.InEgg:
                lastModified = modificationTimeFor(plugin.Path)
                if sources and all(lastModified <= source.LastModified for source in sources.values()):
                    log.info('No modifications for zip file "%s" in %s', plugin.Path, plugin.Name)
                    continue
                scanner = scanZip(plugin.Path)
            else:
                lastModified, scanner = None, scanFolder(plugin.Path)
            
            self._persist(sources, scanner, plugin.Path, lastModified, None, plugin.Id)
            
    # ----------------------------------------------------------------
    
    def _persist(self, sources, scanner, path, lastModified, componentId, pluginId):
        '''
        Persist the sources and messages. 
        '''
        for filePath, method, extractor in scanner:
            assert method in TYPES, 'Invalid method %s' % method
            source = sources.get(filePath)
            if not lastModified:
                lastModified = modificationTimeFor(path)
                if source:
                    assert isinstance(source, Source)
                    if lastModified <= source.LastModified:
                        log.info('No modifications for file "%s"', path)
                        continue
            messages = None
            for locale, domain, text, context, lineno, comments in extractor:
                if not source:
                    source = Source()
                    source.Component = componentId
                    source.Plugin = pluginId
                    source.Path = filePath
                    source.Type = method
                    source.LastModified = lastModified
                    self.sourceService.insert(source)
                    sources[filePath] = source
                    
                if messages is None: messages = {msg.Singular:msg for msg in self.messageService.getMessages(source.Id)}
                
                if isinstance(text, str): singular, plurals = text, None
                elif len(text) == 1: singular, plurals = text[0], None
                else: singular, plurals = text[0], list(text[1:])
                
                msg = messages.get(singular)
                if not msg:
                    msg = Message()
                    msg.Source = source.Id
                    msg.Locale = locale
                    msg.Domain = domain
                    msg.Singular = singular
                    msg.Plural = plurals
                    msg.Context = context
                    msg.LineNumber = lineno
                    msg.Comments = '\n'.join(comments)
                    
                    self.messageService.insert(msg)
                    messages[singular] = msg
    
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
        overall = dict(domain=DOMAIN_DEFAULT, locale=LOCALE_DEFAULT)
        for pattern, method in METHOD_MAP:
            if pathmatch(pattern, name):
                filePath = zipFilePath + '/' + name
                def openZip():
                    with zipFile.open(name, 'r') as f:
                        return BytesIO(f.read())
                yield filePath, method, process(openZip, method, overall)

def scanFolder(folderPath):
    '''
    Scan a folder that is found on the provided path.
    
    @param folderPath: string
        The folder path.
    @return: tuple(string, string, generator)
        Returns a tuple containing: (filePath, method, generator(@see: process))
    '''
    for root, dirnames, filenames in os.walk(folderPath):
        for subdir in dirnames:
            if subdir.startswith('.'): dirnames.remove(subdir)
        dirnames.sort()
        filenames.sort()
        for name in filenames:
            name = path.relpath(os.path.join(root, name)).replace(os.sep, '/')
            overall = dict(domain=DOMAIN_DEFAULT, locale=LOCALE_DEFAULT)
            for pattern, method in METHOD_MAP:
                if pathmatch(pattern, name):
                    filePath = name.replace('/', os.sep)
                    yield filePath, method, process(partial(open, name, 'rb'), method, overall)

def process(openFile, method, overall):
    '''
    Process the content of the file generated by the openFile.
    
    @param openFile: callable
        The open file function.
    @param method: string
        The method used for processing the file.
    @param overall: dictionary{string, string}
        Contains the overall data, like 'domain' and 'locale'
    @param message: string|list[string]|tuple(string)
        The message to be processed.
    @return: tuple(string, string, string|tuple(string), string, integer, string)
        Returns a tuple containing: (locale, domain, message, context, lineno, comments)
    '''
    assert callable(openFile), 'Invalid open file function %s' % openFile
    assert isinstance(method, str), 'Invalid method %s' % method
    assert isinstance(overall, dict), 'Invalid overall %s' % overall

    with openFile() as fileObj:
        for fname, lineno, message, comments in extract(method, fileObj):
            domain, cntxt = overall['domain'], None
            if fname == 'textlocale':
                assert isinstance(message, str), 'Invalid message %s' % message
                overall['locale'] = message
                continue
            elif fname == 'textdomain':
                assert isinstance(message, str), 'Invalid message %s' % message
                overall['domain'] = message
                continue
            elif fname == 'dgettext': domain, message = message
            elif fname == 'dngettext': domain, *message = message
            elif fname in ('pgettext', 'C_', 'NC_'): cntxt, message = message
            elif fname == 'dpgettext': cntxt, domain, message = message
            elif fname == 'npgettext': cntxt, *message = message
            elif fname == 'dnpgettext': cntxt, domain, *message = message
            
            locale = overall['locale']
        
            assert log.debug('(%s) %s -> %s (%s) #%s' % (locale, domain, message, cntxt, comments)) or True
            yield locale, domain, message, cntxt, lineno, comments

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
        try:
            from pkg_resources import working_set
        except ImportError:
            # pkg_resources is not available, so we resort to looking up the
            # builtin extractors directly
            builtin = {'ignore': extract_nothing, 'python': extract_python}
            func = builtin.get(method)
        else:
            for entry_point in working_set.iter_entry_points(GROUP_NAME, method):
                func = entry_point.load(require=True)
                break
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
