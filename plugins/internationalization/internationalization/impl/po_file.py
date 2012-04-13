'''
Created on Mar 9, 2012

@package: internationalization
@copyright: 2012 Sourcefabric o.p.s.
@license: http://www.gnu.org/licenses/gpl-3.0.txt
@author: Mugur Rus

Implementation for the PO file management.
'''

from ally.container import wire
from ally.container.ioc import injected
from ally.exception import InputError
from ally.internationalization import _
from cdm.spec import ICDM, PathNotFound
from internationalization.api.po_file import IPOFileService
from internationalization.core.spec import IPOFileManager, InvalidLocaleError
from introspection.api.plugin import IPluginService, Plugin
from ally.api.model import Content
import codecs

# --------------------------------------------------------------------

@injected
class POFileServiceCDM(IPOFileService):
    '''
    Implementation for @see: IPOService
    '''

    default_charset = 'UTF-8'; wire.config('default_charset', doc='''
    The default character set to use whenever a PO file is uploaded ant the character set of the content is not
    specified''')

    poFileManager = IPOFileManager; wire.entity('poFileManager')
    cdmPO = ICDM; wire.entity('cdmPO')
    pluginService = IPluginService; wire.entity('pluginService')

    def __init__(self):
        assert isinstance(self.default_charset, str), 'Invalid default charset %s' % self.default_charset
        assert isinstance(self.poFileManager, IPOFileManager), 'Invalid PO file manager %s' % self.poFileManager
        assert isinstance(self.cdmPO, ICDM), 'Invalid PO CDM %s' % self.cdmPO
        assert isinstance(self.pluginService, IPluginService), 'Invalid plugin service %s' % self.pluginService

    def getGlobalPOFile(self, locale):
        '''
        @see: IPOService.getGlobalPOFile
        '''
        path = self._cdmPath(locale)
        try:
            try: cdmFileTimestamp = self.cdmPO.getTimestamp(path)
            except PathNotFound: republish = True
            else:
                mngFileTimestamp = self.poFileManager.getGlobalPOTimestamp(locale)
                republish = False if mngFileTimestamp is None else cdmFileTimestamp < mngFileTimestamp

            if republish:
                self.cdmPO.publishFromFile(path, self.poFileManager.getGlobalPOFile(locale))
        except InvalidLocaleError: raise InputError(_('Invalid locale %(locale)s') % dict(locale=locale))
        return self.cdmPO.getURI(path, 'http')

    def getComponentPOFile(self, component, locale):
        '''
        @see: IPOService.getComponentPOFile
        '''
        path = self._cdmPath(locale, component=component)
        try:
            try: cdmFileTimestamp = self.cdmPO.getTimestamp(path)
            except PathNotFound: republish = True
            else:
                mngFileTimestamp = self.poFileManager.getComponentPOTimestamp(component, locale)
                republish = False if mngFileTimestamp is None else cdmFileTimestamp < mngFileTimestamp

            if republish:
                self.cdmPO.publishFromFile(path, self.poFileManager.getComponentPOFile(component, locale))
        except InvalidLocaleError: raise InputError(_('Invalid locale %(locale)s') % dict(locale=locale))
        return self.cdmPO.getURI(path, 'http')

    def getPluginPOFile(self, plugin, locale):
        '''
        @see: IPOService.getPluginPOFile
        '''
        pluginObj = self.pluginService.getById(plugin)
        assert isinstance(pluginObj, Plugin)
        if pluginObj.Component: return self.getComponentPOFile(pluginObj.Component, locale)

        path = self._cdmPath(locale, plugin=plugin)
        try:
            try: cdmFileTimestamp = self.cdmPO.getTimestamp(path)
            except PathNotFound: republish = True
            else:
                mngFileTimestamp = self.poFileManager.getPluginPOTimestamp(plugin, locale)
                republish = False if mngFileTimestamp is None else cdmFileTimestamp < mngFileTimestamp

            if republish:
                self.cdmPO.publishFromFile(path, self.poFileManager.getPluginPOFile(plugin, locale))
        except InvalidLocaleError: raise InputError(_('Invalid locale %(locale)s') % dict(locale=locale))
        return self.cdmPO.getURI(path, 'http')

    # ----------------------------------------------------------------

    def updateGlobalPOFile(self, locale, poFile):
        '''
        @see: IPOService.updateGlobalPOFile
        '''
        assert isinstance(poFile, Content), 'Invalid PO content %s' % poFile
        # Convert the byte file to text file
        poFile = codecs.getreader(poFile.getCharSet() or self.default_charset)(poFile)
        self.poFileManager.updateGlobalPOFile(locale, poFile)

    def updateComponentPOFile(self, poFile, component, locale):
        '''
        @see: IPOService.updateComponentPOFile
        '''
        self.poFileManager.updateComponentPOFile(poFile, component, locale)

    def updatePluginPOFile(self, poFile, plugin, locale):
        '''
        @see: IPOService.updatePluginPOFile
        '''
        self.poFileManager.updatePluginPOFile(poFile, plugin, locale)

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
