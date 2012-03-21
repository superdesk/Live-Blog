'''
Created on Mar 13, 2012

@package: internationalization
@copyright: 2012 Sourcefabric o.p.s.
@license: http://www.gnu.org/licenses/gpl-3.0.txt
@author: Mugur Rus

API specifications for PO file management.
'''

from introspection.api.plugin import Plugin
from introspection.api.component import Component

# --------------------------------------------------------------------

class IPOFileManager:
    '''
    The PO file manager.
    '''

    def poFileTimestamp(self, locale:str, component:Component.Id=None, plugin:Plugin.Id=None):
        '''
        Returns the timestamp of the last update for the PO file identified by
        the given locale and/or component/plugin.

        @param locale: string
            The locale identifying the translation file.
        @param component: Component.Id
            The component identifying the translation file.
        @param plugin: Plugin.Id
            The plugin identifying the translation file.
        '''

    def getGlobalPOFile(self, locale:str) -> str:
        '''
        Provides the messages for the whole application and the given locale.

        @param locale: string
            The locale for which to return the translation.
        @return: string
            The path to the temporary PO file.
        '''

    def getComponentPOFile(self, component:Component.Id, locale:str) -> str:
        '''
        Provides the messages for the given component and the given locale.

        @param locale: string
            The locale for which to return the translation.
        @param component: Component.Id
            The component for which to return the translation.
        @return: string
            The path to the temporary PO file.
        '''

    def getPluginPOFile(self, plugin:Plugin.Id, locale:str) -> str:
        '''
        Provides the messages for the given plugin and the given locale.

        @param locale: string
            The locale for which to return the translation.
        @param plugin: Plugin.Id
            The plugin for which to return the translation.
        @return: string
            The path to the temporary PO file.
        '''

    def updateGlobalPOFile(self, poFile, locale:str):
        '''
        Updates the messages for all components / plugins and the given locale.

        @param poFile: file like object
            The source PO file from which to read the translation.
        @param locale: string
            The locale for which to update the translation.
        '''

    def updateComponentPOFile(self, poFile, component:Component.Id, locale:str):
        '''
        Updates the messages for the given component and the given locale.

        @param poFile: file like object
            The source PO file from which to read the translation.
        @param locale: string
            The locale for which to update the translation.
        @param component: Component.Id
            The component for which to update the translation.
        '''

    def updatePluginPOFile(self, poFile, plugin:Plugin.Id, locale:str):
        '''
        Updates the messages for the given plugin and the given locale.

        @param poFile: file like object
            The source PO file from which to read the translation.
        @param locale: string
            The locale for which to update the translation.
        @param plugin: Plugin.Id
            The plugin for which to update the translation.
        '''
