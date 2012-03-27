'''
Created on Mar 9, 2012

@package: internationalization
@copyright: 2012 Sourcefabric o.p.s.
@license: http://www.gnu.org/licenses/gpl-3.0.txt
@author: Mugur Rus

Implementation for the PO file management.
'''

from internationalization.api.po_file import IPOFileService
from ally.container.ioc import injected
from internationalization.core.spec import IPOFileManager
from cdm.spec import ICDM, PathNotFound

# --------------------------------------------------------------------

@injected
class POFileServiceCDM(IPOFileService):
    '''
    Implementation for @see: IPOService
    '''

    poManager = IPOFileManager

    poCdm = ICDM

    def getGlobalPOFile(self, locale):
        '''
        @see: IPOService.getGlobalPOFile
        '''
        path = self._cdmPath(locale)
        try:
            cdmFileTimestamp = self.poCdm.getTimestamp(path)
            mngFileTimestamp = self.poManager.getGlobalPOTimestamp(locale)
            republish = cdmFileTimestamp < mngFileTimestamp
        except PathNotFound:
            republish = True
        if republish:
            self.poCdm.publishFromFile(path, self.poManager.getGlobalPOFile(locale))
        return self.poCdm.getURI(path, 'http')

    def getComponentPOFile(self, component, locale):
        '''
        @see: IPOService.getComponentPOFile
        '''
        path = self._cdmPath(locale, component)
        try:
            cdmFileTimestamp = self.poCdm.getTimestamp(path)
            mngFileTimestamp = self.poManager.getComponentPOTimestamp(component, locale)
            republish = cdmFileTimestamp < mngFileTimestamp
        except PathNotFound:
            republish = True
        if republish:
            self.poCdm.publishFromFile(path, self.poManager.getComponentPOFile(component, locale))
        return self.poCdm.getURI(path, 'http')

    def getPluginPOFile(self, plugin, locale):
        '''
        @see: IPOService.getPluginPOFile
        '''
        path = self._cdmPath(locale, plugin=plugin)
        try:
            cdmFileTimestamp = self.poCdm.getTimestamp(path)
            mngFileTimestamp = self.poManager.getPluginPOTimestamp(plugin, locale)
            republish = cdmFileTimestamp < mngFileTimestamp
        except PathNotFound:
            republish = True
        if republish:
            self.poCdm.publishFromFile(path, self.poManager.getPluginPOFile(plugin, locale))
        return self.poCdm.getURI(path, 'http')

    def updateGlobalPOFile(self, poFile, locale:str):
        '''
        @see: IPOService.updateGlobalPOFile
        '''
        self.poManager.updateGlobalPOFile(poFile, locale)

    def updateComponentPOFile(self, poFile, component, locale):
        '''
        @see: IPOService.updateComponentPOFile
        '''
        self.poManager.updateComponentPOFile(poFile, component, locale)

    def updatePluginPOFile(self, poFile, plugin, locale):
        '''
        @see: IPOService.updatePluginPOFile
        '''
        self.poManager.updatePluginPOFile(poFile, plugin, locale)

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
