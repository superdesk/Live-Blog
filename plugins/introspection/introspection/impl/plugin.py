'''
Created on Mar 4, 2012

@package: introspection
@copyright: 2011 Sourcefabric o.p.s.
@license: http://www.gnu.org/licenses/gpl-3.0.txt
@author: Gabriel Nistor

Implementation for the components introspection.
'''

from ally.internationalization import _
from ally.api.model import Part
from ally.container.aop import modulesIn
from ally.container.ioc import injected
from ally.exception import InputError, Ref
from ally.support.api.util_service import trimIter
from introspection.api.plugin import IPluginService, Plugin
from os import path
import sys
from introspection.api.component import IComponentService, QComponent
from ally.container import wire

# --------------------------------------------------------------------

@injected
class PluginService(IPluginService):
    '''
    Provides the implementation for @see: IPluginService.
    '''

    package = '__plugin__'
    # The top package where the plugins are configured
    default_locale = 'en'
    # The default locale in which the plugins are defined.

    componentService = IComponentService; wire.entity('componentService')

    def __init__(self):
        '''
        Constructs the plugins service.
        '''
        assert isinstance(self.package, str), 'Invalid package pattern %s' % self.package
        assert isinstance(self.default_locale, str), 'Invalid locale %s' % self.default_locale
        assert isinstance(self.componentService, IComponentService), 'Invalid component service %s' % self.componentService

    def getById(self, id):
        '''
        @see: IPluginService.getById
        '''
        assert isinstance(id, str), 'Invalid id %s' % id
        modules = modulesIn('%s.%s' % (self.package, id)).asList()
        if len(modules) != 1: raise InputError(Ref(_('Invalid plugin id'), ref=Plugin.Id))
        return self.pluginFor(modules[0])

    def getPlugins(self, offset=None, limit=None):
        '''
        @see: IPluginService.getPlugins
        '''
        modules = modulesIn('%s.*' % self.package).asList()
        modules.sort()

        components = {cmp.Path:cmp.Id for cmp in self.componentService.getComponents()}
        plugins = (self.pluginFor(module, components) for module in modules)

        return Part(trimIter(plugins, len(modules), offset, limit), len(modules))

    # ----------------------------------------------------------------

    def pluginFor(self, module, components=None):
        '''
        Create a plugin based on the provided module.
        
        @param module: string
            The module to create a plugin for.
        @param components: dictionary{string, string}|None
            A dictionary having as a key the compoenent path and as a value the compoenent id.
        @return: Plugin
            The plugin reflecting the module.
        '''
        assert isinstance(module, str), 'Invalid module %s' % module

        c = Plugin()
        c.Id = module[len(self.package) + 1:]

        m = sys.modules.get(module)
        if m:
            c.Loaded = True
            c.Name = getattr(m, 'NAME', None)
            c.Group = getattr(m, 'GROUP', None)
            c.Version = getattr(m, 'VERSION', None)
            c.Locale = getattr(m, 'LANGUAGE', self.default_locale)
            c.Description = getattr(m, 'DESCRIPTION', None)
            c.Path = path.relpath(path.dirname(path.dirname(path.dirname(m.__file__))))
            c.InEgg = not path.isfile(m.__file__)
        else:
            c.Loaded = False
        if components is None:
            try: c.Component = next(iter(self.componentService.getComponents(limit=1, q=QComponent(path=c.Path)))).Id
            except StopIteration: pass
        else:
            assert isinstance(components, dict), 'Invalid components %s' % components
            c.Component = components.get(c.Path, None)

        return c
