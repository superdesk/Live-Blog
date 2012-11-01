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
from ally.container import wire
from ally.container.ioc import injected
from ally.container.support import setup
from ally.exception import InputError
from ally.internationalization import _
from cdm.spec import ICDM, PathNotFound
from datetime import datetime
from internationalization.api.json_locale import IJSONLocaleFileService
from internationalization.core.spec import IPOFileManager, InvalidLocaleError
from json.encoder import JSONEncoder
from io import BytesIO
from sys import getdefaultencoding

# --------------------------------------------------------------------

@injected
@setup(IJSONLocaleFileService)
class JSONFileService(IJSONLocaleFileService):
    '''
    Implementation for @see: IJSONLocaleFileService
    '''

    default_charset = 'UTF-8'; wire.config('default_charset', doc='''
    The default character set to use whenever a JSON locale file is uploaded and
    the character set of the content is not specified''')

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

    def getGlobalJSONFile(self, locale, scheme):
        '''
        @see: IPOService.getGlobalPOFile
        '''
        path = self._cdmPath(locale)
        try:
            try: cdmFileTimestamp = self.cdmLocale.getTimestamp(path)
            except PathNotFound: republish = True
            else:
                mngFileTimestamp = self.poFileManager.getGlobalPOTimestamp(locale)
                republish = False if mngFileTimestamp is None else cdmFileTimestamp < mngFileTimestamp

            if republish:
                self.cdmLocale.publishContent(path, JSONEncoder().encode(self.poFileManager.getGlobalAsDict(locale)))
        except InvalidLocaleError: raise InputError(_('Invalid locale %(locale)s') % dict(locale=locale))
        return self.cdmLocale.getURI(path, scheme)

    def getComponentJSONFile(self, component, locale, scheme):
        '''
        @see: IPOService.getComponentPOFile
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
                self.cdmLocale.publishContent(path, JSONEncoder().encode(self.poFileManager.getComponentAsDict(component, locale)))
        except InvalidLocaleError: raise InputError(_('Invalid locale %(locale)s') % dict(locale=locale))
        return self.cdmLocale.getURI(path, scheme)

    def getPluginJSONFile(self, plugin, locale, scheme):
        '''
        @see: IPOService.getPluginPOFile
        '''
        pluginObj = self.pluginService.getById(plugin)
        assert isinstance(pluginObj, Plugin)
        if pluginObj.Component: return self.getComponentJSONFile(pluginObj.Component, locale, scheme)

        path = self._cdmPath(locale, plugin=plugin)
        try:
            try: cdmFileTimestamp = self.cdmLocale.getTimestamp(path)
            except PathNotFound: republish = True
            else:
                mngFileTimestamp = mngFileTimestamp = max(self.poFileManager.getGlobalPOTimestamp(locale) or datetime.min,
                                                          self.poFileManager.getPluginPOTimestamp(plugin, locale) or datetime.min)
                republish = False if mngFileTimestamp is None else cdmFileTimestamp < mngFileTimestamp

            if republish:
                jsonString = JSONEncoder().encode(self.poFileManager.getPluginAsDict(plugin, locale))
                self.cdmLocale.publishContent(path, BytesIO(bytes(jsonString, getdefaultencoding())))
        except InvalidLocaleError: raise InputError(_('Invalid locale %(locale)s') % dict(locale=locale))
        return self.cdmLocale.getURI(path, scheme)

    # ----------------------------------------------------------------

    def _cdmPath(self, locale, component=None, plugin=None):
        '''
        Returns the path to the CDM JSON file corresponding to the given locale and / or
        component / plugin. If no component of plugin was specified it returns the
        name of the global JSON file.

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
        return '%s.json' % '-'.join(path)
