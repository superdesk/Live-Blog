'''
Created on Mar 9, 2012

@package: internationalization
@copyright: 2012 Sourcefabric o.p.s.
@license: http://www.gnu.org/licenses/gpl-3.0.txt
@author: Mugur Rus

Implementation for the PO file management.
'''

from admin.introspection.api.component import IComponentService
from admin.introspection.api.plugin import IPluginService, Plugin
from ally.api.model import Content
from ally.container import wire
from ally.container.ioc import injected
from ally.container.support import setup
from ally.exception import InputError, DevelError
from ally.internationalization import _, C_
from cdm.spec import ICDM, PathNotFound
from datetime import datetime
from internationalization.api.po_file import IPOFileService
from internationalization.core.spec import IPOFileManager, InvalidLocaleError
import codecs

# --------------------------------------------------------------------

@injected
@setup(IPOFileService)
class POFileService(IPOFileService):
    '''
    Implementation for @see: IPOFileService
    '''

    default_charset = 'UTF-8'; wire.config('default_charset', doc='''
    The default character set to use whenever a PO file is uploaded and the character
    set of the content is not specified''')

    poFileManager = IPOFileManager; wire.entity('poFileManager')
    cdmLocale = ICDM; wire.entity('cdmLocale')
    pluginService = IPluginService; wire.entity('pluginService')
    componentService = IComponentService; wire.entity('componentService')

    def __init__(self):
        assert isinstance(self.default_charset, str), 'Invalid default charset %s' % self.default_charset
        assert isinstance(self.poFileManager, IPOFileManager), 'Invalid PO file manager %s' % self.poFileManager
        assert isinstance(self.cdmLocale, ICDM), 'Invalid PO CDM %s' % self.cdmLocale
        assert isinstance(self.pluginService, IPluginService), 'Invalid plugin service %s' % self.pluginService
        assert isinstance(self.componentService, IComponentService), 'Invalid component service %s' % self.componentService

    def getGlobalPOFile(self, locale, scheme):
        '''
        @see: IPOFileService.getGlobalPOFile
        '''
        path = self._cdmPath(locale)
        try:
            try: cdmFileTimestamp = self.cdmLocale.getTimestamp(path)
            except PathNotFound: republish = True
            else:
                mngFileTimestamp = self.poFileManager.getGlobalPOTimestamp(locale)
                republish = False if mngFileTimestamp is None else cdmFileTimestamp < mngFileTimestamp

            if republish:
                self.cdmLocale.publishFromFile(path, self.poFileManager.getGlobalPOFile(locale))
        except InvalidLocaleError: raise InputError(_('Invalid locale %(locale)s') % dict(locale=locale))
        return self.cdmLocale.getURI(path, scheme)

    def getComponentPOFile(self, component, locale, scheme):
        '''
        @see: IPOFileService.getComponentPOFile
        '''
        self.componentService.getById(component)
        path = self._cdmPath(locale, component=component)
        try:
            try: cdmFileTimestamp = self.cdmLocale.getTimestamp(path)
            except PathNotFound: republish = True
            else:
                mngFileTimestamp = max(self.poFileManager.getGlobalPOTimestamp(locale) or datetime.min,
                                       self.poFileManager.getComponentPOTimestamp(component, locale) or datetime.min)
                republish = False if mngFileTimestamp is None else cdmFileTimestamp < mngFileTimestamp

            if republish:
                self.cdmLocale.publishFromFile(path, self.poFileManager.getComponentPOFile(component, locale))
        except InvalidLocaleError: raise InputError(_('Invalid locale %(locale)s') % dict(locale=locale))
        return self.cdmLocale.getURI(path, scheme)

    def getPluginPOFile(self, plugin, locale, scheme):
        '''
        @see: IPOFileService.getPluginPOFile
        '''
        pluginObj = self.pluginService.getById(plugin)
        assert isinstance(pluginObj, Plugin)
        if pluginObj.Component: return self.getComponentPOFile(pluginObj.Component, locale, scheme)

        path = self._cdmPath(locale, plugin=plugin)
        try:
            try: cdmFileTimestamp = self.cdmLocale.getTimestamp(path)
            except PathNotFound: republish = True
            else:
                mngFileTimestamp = mngFileTimestamp = max(self.poFileManager.getGlobalPOTimestamp(locale) or datetime.min,
                                                          self.poFileManager.getPluginPOTimestamp(plugin, locale) or datetime.min)
                republish = False if mngFileTimestamp is None else cdmFileTimestamp < mngFileTimestamp

            if republish:
                self.cdmLocale.publishFromFile(path, self.poFileManager.getPluginPOFile(plugin, locale))
        except InvalidLocaleError: raise InputError(_('Invalid locale %(locale)s') % dict(locale=locale))
        return self.cdmLocale.getURI(path, scheme)

    # ----------------------------------------------------------------

    def updateGlobalPOFile(self, locale, poFile):
        '''
        @see: IPOFileService.updateGlobalPOFile
        '''
        assert isinstance(poFile, Content), 'Invalid PO content %s' % poFile
        # Convert the byte file to text file
        poFile = codecs.getreader(poFile.charSet or self.default_charset)(poFile)
        try: self.poFileManager.updateGlobalPOFile(locale, poFile)
        except UnicodeDecodeError: raise InvalidPOFile(poFile)
        if poFile.next(): raise ToManyFiles()

    def updateComponentPOFile(self, component, locale, poFile):
        '''
        @see: IPOFileService.updateComponentPOFile
        '''
        self.componentService.getById(component)
        assert isinstance(poFile, Content), 'Invalid PO content %s' % poFile
        # Convert the byte file to text file
        poFile = codecs.getreader(poFile.charSet or self.default_charset)(poFile)
        try: self.poFileManager.updateComponentPOFile(component, locale, poFile)
        except UnicodeDecodeError: raise InvalidPOFile(poFile)
        if poFile.next(): raise ToManyFiles()

    def updatePluginPOFile(self, plugin, locale, poFile):
        '''
        @see: IPOFileService.updatePluginPOFile
        '''
        assert isinstance(poFile, Content), 'Invalid PO content %s' % poFile
        pluginObj = self.pluginService.getById(plugin)
        assert isinstance(pluginObj, Plugin)
        if pluginObj.Component: return self.updateComponentPOFile(pluginObj.Component, locale, poFile)
        # Convert the byte file to text file
        poFile = codecs.getreader(poFile.charSet or self.default_charset)(poFile)
        try: self.poFileManager.updatePluginPOFile(plugin, locale, poFile)
        except UnicodeDecodeError: raise InvalidPOFile(poFile)
        if poFile.next(): raise ToManyFiles()

    # ----------------------------------------------------------------

    def _cdmPath(self, locale, component=None, plugin=None):
        '''
        Returns the path to the CDM PO file corresponding to the given locale and / or
        component / plugin. If no component of plugin was specified it returns the
        name of the global PO file.
        
        @param locale: string
            The locale.
        @param component: string
            The component id.
        @param plugin: string
            The plugin id.
        @return: string
            The file path.
        '''
        assert isinstance(locale, str), 'Invalid locale %s' % locale

        path = []
        if component:
            path.append('component')
            path.append(component)
        elif plugin:
            path.append('plugin')
            path.append(plugin)
        else:
            path.append('global')
        path.append(locale)
        return '%s.po' % '-'.join(path)


# --------------------------------------------------------------------

# Raised when there is an invalid PO content
InvalidPOFile = lambda poFile:InputError(_('Invalid content for PO file %(file)s') % dict(file=poFile.getName() or
                                                                                    C_('Unknown file name', 'unknown')))

# Raised if there are to many files provided in content.
ToManyFiles = lambda :DevelError('To many PO files, only one accepted')
