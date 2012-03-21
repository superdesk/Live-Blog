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

# --------------------------------------------------------------------

@injected
class POFileServiceAlchemy(IPOFileService):
    '''
    Implementation for @see: IPOService
    '''

    def __init__(self):
        '''
        '''

    def getGlobalPOFile(self, language):
        '''
        @see: IPOService.getGlobalPOFile
        '''

    def getComponentPOFile(self, component, locale):
        '''
        @see: IPOService.getComponentPOFile
        '''

    def getPluginPOFile(self, plugin, locale):
        '''
        @see: IPOService.getPluginPOFile
        '''

    def updateGlobalPOFile(self, poFile, locale:str):
        '''
        @see: IPOService.updateGlobalPOFile
        '''

    def updateComponentPOFile(self, poFile, component, locale):
        '''
        @see: IPOService.updateComponentPOFile
        '''

    def updatePluginPOFile(self, poFile, plugin, locale):
        '''
        @see: IPOService.updatePluginPOFile
        '''
