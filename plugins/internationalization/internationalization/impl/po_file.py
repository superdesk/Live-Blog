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
from ally.container import wire
from cdm.spec import ICDM, PathNotFound

# --------------------------------------------------------------------

@injected
class POFileServiceAlchemy(IPOFileService):
    '''
    Implementation for @see: IPOService
    '''

    po_file_manager = IPOFileManager; wire.entity('po_file_manager')

    po_cdm = ICDM; wire.entity('po_cdm')

    def __init__(self):
        '''
        '''

    def getGlobalPOFile(self, locale):
        '''
        @see: IPOService.getGlobalPOFile
        '''
        path = self._cdmPath(locale)
        try:
            cdmFileTimestamp = self.po_cdm.getTimestamp(path)
        except PathNotFound:
            return self.po_file_manager.getGlobalPOFile(locale)
        mngFileTimestamp = self.po_file_manager.poFileTimestamp(locale)
        if cdmFileTimestamp < mngFileTimestamp:
            return self.po_file_manager.getGlobalPOFile(locale)

    def getComponentPOFile(self, component, locale):
        '''
        @see: IPOService.getComponentPOFile
        '''
        path = self._cdmPath(locale, component)
        try:
            cdmFileTimestamp = self.po_cdm.getTimestamp(path)
        except PathNotFound:
            return self.po_file_manager.getComponentPOFile(component, locale)
        mngFileTimestamp = self.po_file_manager.poFileTimestamp(locale)
        if cdmFileTimestamp < mngFileTimestamp:
            return self.po_file_manager.getComponentPOFile(component, locale)

    def getPluginPOFile(self, plugin, locale):
        '''
        @see: IPOService.getPluginPOFile
        '''
        path = self._cdmPath(locale, plugin=plugin)
        try:
            cdmFileTimestamp = self.po_cdm.getTimestamp(path)
        except PathNotFound:
            return self.po_file_manager.getPluginPOFile(plugin, locale)
        mngFileTimestamp = self.po_file_manager.poFileTimestamp(locale)
        if cdmFileTimestamp < mngFileTimestamp:
            return self.po_file_manager.getPluginPOFile(plugin, locale)

    def updateGlobalPOFile(self, poFile, locale:str):
        '''
        @see: IPOService.updateGlobalPOFile
        '''
        self.po_file_manager.updateGlobalPOFile(poFile, locale)

    def updateComponentPOFile(self, poFile, component, locale):
        '''
        @see: IPOService.updateComponentPOFile
        '''
        self.po_file_manager.updateComponentPOFile(poFile, component, locale)

    def updatePluginPOFile(self, poFile, plugin, locale):
        '''
        @see: IPOService.updatePluginPOFile
        '''
        self.po_file_manager.updatePluginPOFile(poFile, plugin, locale)

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
