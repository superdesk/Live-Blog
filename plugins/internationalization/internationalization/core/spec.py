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
import abc

# --------------------------------------------------------------------

class IPOFileManager(metaclass=abc.ABCMeta):
    '''
    The PO file manager: processes and returns the PO global, component or plugin
    PO files.
    '''

    @abc.abstractmethod
    def getGlobalPOTimestamp(self, locale:str=None):
        '''
        Returns the timestamp of the last update for the PO file identified by
        the given locale.

        @param locale: string
            The locale identifying the translation file.
        '''

    @abc.abstractmethod
    def getComponentPOTimestamp(self, component:Component.Id, locale:str=None):
        '''
        Returns the timestamp of the last update for the PO file identified by
        the given component and locale.

        @param component: Component.Id
            The component identifying the translation file.
        @param locale: string
            The locale identifying the translation file.
        '''

    @abc.abstractmethod
    def getPluginPOTimestamp(self, plugin:Plugin.Id, locale:str=None):
        '''
        Returns the timestamp of the last update for the PO file identified by
        the given plugin and locale.

        @param plugin: Plugin.Id
            The plugin identifying the translation file.
        @param locale: string
            The locale identifying the translation file.
        '''

    @abc.abstractmethod
    def getGlobalPOFile(self, locale:str=None) -> str:
        '''
        Provides the messages for the whole application and the given locale.

        @param locale: string
            The locale for which to return the translation.
        @return: string
            The path to the temporary PO file.
        '''

    @abc.abstractmethod
    def getComponentPOFile(self, component:Component.Id, locale:str=None) -> str:
        '''
        Provides the messages for the given component and the given locale.

        @param component: Component.Id
            The component for which to return the translation.
        @param locale: string
            The locale for which to return the translation.
        @return: string
            The path to the temporary PO file.
        '''

    @abc.abstractmethod
    def getPluginPOFile(self, plugin:Plugin.Id, locale:str=None) -> str:
        '''
        Provides the messages for the given plugin and the given locale.

        @param plugin: Plugin.Id
            The plugin for which to return the translation.
        @param locale: string
            The locale for which to return the translation.
        @return: string
            The path to the temporary PO file.
        '''

    @abc.abstractmethod
    def updateGlobalPOFile(self, poFile, locale:str):
        '''
        Updates the messages for all components / plugins and the given locale.

        @param poFile: file like object
            The source PO file from which to read the translation.
        @param locale: string
            The locale for which to update the translation.
        '''

    @abc.abstractmethod
    def updateComponentPOFile(self, poFile, component:Component.Id, locale:str):
        '''
        Updates the messages for the given component and the given locale.

        @param poFile: file like object
            The source PO file from which to read the translation.
        @param component: Component.Id
            The component for which to update the translation.
        @param locale: string
            The locale for which to update the translation.
        '''

    @abc.abstractmethod
    def updatePluginPOFile(self, poFile, plugin:Plugin.Id, locale:str):
        '''
        Updates the messages for the given plugin and the given locale.

        @param poFile: file like object
            The source PO file from which to read the translation.
        @param plugin: Plugin.Id
            The plugin for which to update the translation.
        @param locale: string
            The locale for which to update the translation.
        '''
