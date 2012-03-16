'''
Created on Mar 9, 2012

@package: internationalization
@copyright: 2012 Sourcefabric o.p.s.
@license: http://www.gnu.org/licenses/gpl-3.0.txt
@author: Mugur Rus

API specifications for PO file management.
'''

from ally.api.config import service, call
from ally.api.type import Iter, Count, List
from introspection.api.plugin import Plugin
from introspection.api.component import Component

# --------------------------------------------------------------------

@service
class IPOFileService:
    '''
    The PO file management service.
    '''

    def getGlobalPOFile(self, language:str) -> str:
        '''
        Provides the messages for the whole application.
        '''

    def getComponentPOFile(self, component:Component.Id, language:str) -> str:
        '''
        Provides the messages for the given component.
        '''

    def getPluginPOFile(self, plugin:Plugin.Id, language:str) -> str:
        '''
        Provides the messages for the given plugin.
        '''

    def updateGlobalPOFile(self, language:str) -> str:
        '''
        Updates the messages for all components and plugins.
        '''

    def updateComponentPOFile(self, component:Component.Id, language:str) -> str:
        '''
        Updates the messages for the given component.
        '''

    def updatePluginPOFile(self, plugin:Plugin.Id, language:str) -> str:
        '''
        Updates the messages for the given plugin.
        '''
