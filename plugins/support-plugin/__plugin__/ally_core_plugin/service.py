'''
Created on Jan 9, 2012

@package ally core plugins
@copyright 2011 Sourcefabric o.p.s.
@license http://www.gnu.org/licenses/gpl-3.0.txt
@author: Gabriel Nistor

Contains the services for the node presenter plugin.
'''

from __plugin__.plugin.registry import services
from ally.container import ioc
from ally_core_plugin.api.plugin import IPluginService
from ally_core_plugin.impl.plugin import PluginService

# --------------------------------------------------------------------

@ioc.entity
def pluginService()->IPluginService: return PluginService()

@ioc.before(services)
def registerService(): services().append(pluginService())
    
