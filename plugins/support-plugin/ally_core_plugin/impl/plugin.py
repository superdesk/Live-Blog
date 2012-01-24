'''
Created on Jan 19, 2012

@package ally core plugins
@copyright 2011 Sourcefabric o.p.s.
@license http://www.gnu.org/licenses/gpl-3.0.txt
@author: Gabriel Nistor

API specifications for plugin support.
'''

from ally.container.aop import modulesIn
from ally.container.ioc import injected
from ally.support.util_sys import isPackage
from ally_core_plugin.api.plugin import IPluginService, Plugin
from os.path import dirname
import sys
from inspect import getdoc

# --------------------------------------------------------------------

@injected
class PluginService(IPluginService):
    '''
    Provides the implementation for @see: IPluginService.
    '''
    
    package = '__plugin__'
    # The package pattern where the plugins are configured.
    
    def __init__(self):
        '''
        Constructs the plugin service.
        '''
        assert isinstance(self.package, str), 'Invalid package pattern %s' % self.package
        self.modulesNames = modulesIn(self.package + '.*').asList()
        self.modulesNames.sort()
    
    def getAllRegisteredPlugins(self, offset=None, limit=None):
        '''
        @see: IPluginService.getAllRegisteredPlugins
        '''
        lpackage = len(self.package) + 1
        for mname in self.modulesNames:
            m = sys.modules.get(mname)
            if m and isPackage(m):
                p = Plugin()
                p.Name = mname[lpackage:].replace('_', ' ')
                p.Location = dirname(dirname(dirname(m.__file__)))
                p.Description = getdoc(m)
                yield p
