'''
Created on Mar 4, 2012

@package: introspection
@copyright: 2011 Sourcefabric o.p.s.
@license: http://www.gnu.org/licenses/gpl-3.0.txt
@author: Gabriel Nistor

Implementation for the components introspection.
'''

from ally.internationalization import _, textdomain
from ally.api.model import Part
from ally.container.aop import modulesIn
from ally.container.ioc import injected
from ally.exception import InputException, Ref
from ally.support.api.util_service import trimIter
from introspection.api.plugin import IPluginService, Plugin
from os import path
import sys

# --------------------------------------------------------------------

textdomain('errors')

# --------------------------------------------------------------------

@injected
class PluginService(IPluginService):
    '''
    Provides the implementation for @see: IPluginService.
    '''
    
    package = '__plugin__'
    # The top package where the plugins are configured
    
    def __init__(self):
        '''
        Constructs the plugins service.
        '''
        assert isinstance(self.package, str), 'Invalid package pattern %s' % self.package
    
    def getById(self, id):
        '''
        @see: IPluginService.getById
        '''
        assert isinstance(id, str), 'Invalid id %s' % id
        modules = modulesIn('%s.%s' % (self.package, id)).asList()
        if len(modules) != 1: raise InputException(Ref(_('Invalid plugin id'), ref=Plugin.Id))
        return self.pluginFor(modules[0])
    
    def getPlugins(self, offset=None, limit=None):
        '''
        @see: IPluginService.getPlugins
        '''
        modules = modulesIn('%s.*' % self.package).asList()
        modules.sort()
        plugins = (self.pluginFor(module) for module in modules)
        return Part(trimIter(plugins, len(modules), offset, limit), len(modules))

    # ----------------------------------------------------------------
    
    def pluginFor(self, module):
        '''
        Create a plugin based on the provided module.
        
        @param module: string
            The module to create a plugin for.
        @return: Plugin
            The plugin reflecting the module.
        '''
        c = Plugin()
        c.Id = module[len(self.package) + 1:]
        
        m = sys.modules.get(module)
        if m:
            c.Loaded = True
            c.Name = getattr(m, 'NAME', None)
            c.Group = getattr(m, 'GROUP', None)
            c.Version = getattr(m, 'VERSION', None)
            c.Description = getattr(m, 'DESCRIPTION', None)
            c.Path = path.relpath(path.dirname(path.dirname(path.dirname(m.__file__))))
            c.InEgg = not path.isfile(m.__file__)
        else:
            c.Loaded = False
            
        return c
