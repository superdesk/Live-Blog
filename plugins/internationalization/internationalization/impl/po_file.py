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
from babel.core import Locale, UnknownLocaleError
from cdm.spec import ICDM, PathNotFound
from internationalization.api.po_file import IPOFileService
from internationalization.core.spec import IPOFileManager

# --------------------------------------------------------------------

@injected
class POFileServiceCDM(IPOFileService):
    '''
    Implementation for @see: IPOService
    '''

    poFileManager = IPOFileManager; wire.entity('poFileManager')
    cdmPO = ICDM; wire.entity('cdmPO')

    def __init__(self):
        assert isinstance(self.poFileManager, IPOFileManager), 'Invalid PO file manager %s' % self.poFileManager
        assert isinstance(self.cdmPO, ICDM), 'Invalid PO CDM %s' % self.cdmPO

    def getGlobalPOFile(self, locale):
        '''
        @see: IPOService.getGlobalPOFile
        '''
        self._validateLocale(locale)
        path = self._cdmPath(locale)
        try:
            cdmFileTimestamp = self.cdmPO.getTimestamp(path)
            mngFileTimestamp = self.poFileManager.getGlobalPOTimestamp(locale)
            republish = cdmFileTimestamp < mngFileTimestamp
        except PathNotFound:
            republish = True

        if republish: self.cdmPO.publishFromFile(path, self.poFileManager.getGlobalPOFile(locale))

        return self.cdmPO.getURI(path, 'http')

    def getComponentPOFile(self, component, locale):
        '''
        @see: IPOService.getComponentPOFile
        '''
        self._validateLocale(locale)
        path = self._cdmPath(locale, component)
        try:
            cdmFileTimestamp = self.cdmPO.getTimestamp(path)
            mngFileTimestamp = self.poFileManager.getComponentPOTimestamp(component, locale)
            republish = cdmFileTimestamp < mngFileTimestamp
        except PathNotFound:
            republish = True
        if republish:
            self.cdmPO.publishFromFile(path, self.poFileManager.getComponentPOFile(component, locale))
        return self.cdmPO.getURI(path, 'http')

    def getPluginPOFile(self, plugin, locale):
        '''
        @see: IPOService.getPluginPOFile
        '''
        self._validateLocale(locale)
        path = self._cdmPath(locale, plugin=plugin)
        try:
            cdmFileTimestamp = self.cdmPO.getTimestamp(path)
            mngFileTimestamp = self.poFileManager.getPluginPOTimestamp(plugin, locale)
            republish = cdmFileTimestamp < mngFileTimestamp
        except PathNotFound:
            republish = True
        if republish:
            self.cdmPO.publishFromFile(path, self.poFileManager.getPluginPOFile(plugin, locale))
        return self.cdmPO.getURI(path, 'http')

    def updateGlobalPOFile(self, poFile, locale):
        '''
        @see: IPOService.updateGlobalPOFile
        '''
        self._validateLocale(locale)
        self.poFileManager.updateGlobalPOFile(poFile, locale)

    def updateComponentPOFile(self, poFile, component, locale):
        '''
        @see: IPOService.updateComponentPOFile
        '''
        self._validateLocale(locale)
        self.poFileManager.updateComponentPOFile(poFile, component, locale)

    def updatePluginPOFile(self, poFile, plugin, locale):
        '''
        @see: IPOService.updatePluginPOFile
        '''
        self._validateLocale(locale)
        self.poFileManager.updatePluginPOFile(poFile, plugin, locale)

    # ----------------------------------------------------------------

    def _validateLocale(self, locale):
        try: Locale.parse(locale)
        except UnknownLocaleError: raise InputError(_('Invalid locale %(locale)s') % dict(locale=locale))

    def _cdmPath(self, locale=None, component=None, plugin=None):
        if component:
            path = component
        elif plugin:
            path = plugin
        else:
            path = 'global'
        if locale:
            path = path + '-' + locale
        path = path + '.po'
        return path
