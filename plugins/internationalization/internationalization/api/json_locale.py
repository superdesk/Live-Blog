'''
Created on May 4, 2012

@package: internationalization
@copyright: 2012 Sourcefabric o.p.s.
@license: http://www.gnu.org/licenses/gpl-3.0.txt
@author: Mugur Rus

API specifications for PO file management.
'''

from admin.api.domain_admin import modelAdmin
from admin.introspection.api.component import Component
from admin.introspection.api.plugin import Plugin
from ally.api.config import service, call
from ally.api.type import Reference, Scheme

# --------------------------------------------------------------------

@modelAdmin(id='Locale')
class JSONLocale:
    '''
    Model for a JSON locale file.
    '''
    Locale = str
    Reference = Reference

# --------------------------------------------------------------------

@service
class IJSONLocaleFileService:
    '''
    The JSON locale service.
    '''

    @call
    def getGlobalJSONFile(self, locale:JSONLocale.Locale, scheme:Scheme) -> JSONLocale.Reference:
        '''
        Provides the messages for the whole application and the given locale in JSON format.
        For format @see: IPOFileManager.getGlobalAsDict.

        @param locale: string
            The locale for which to return the translation.
        @return: string
            The path to the temporary JSON file.
        '''

    @call
    def getComponentJSONFile(self, component:Component.Id, locale:JSONLocale.Locale,
                             scheme:Scheme) -> JSONLocale.Reference:
        '''
        Provides the messages for the given component and the given locale in JSON format.
        For format @see: IPOFileManager.getGlobalAsDict.

        @param component: Component.Id
            The component for which to return the translation.
        @param locale: string
            The locale for which to return the translation.
        @return: string
            The path to the temporary JSON file.
        '''

    @call
    def getPluginJSONFile(self, plugin:Plugin.Id, locale:JSONLocale.Locale,
                          scheme:Scheme) -> JSONLocale.Reference:
        '''
        Provides the messages for the given plugin and the given locale in JSON format.
        For format @see: IPOFileManager.getGlobalAsDict.

        @param locale: string
            The locale for which to return the translation.
        @param plugin: Plugin.Id
            The plugin for which to return the translation.
        @return: string
            The path to the temporary JSON file.
        '''
