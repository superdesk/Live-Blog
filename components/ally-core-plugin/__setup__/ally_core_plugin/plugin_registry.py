'''
Created on Jan 12, 2012

@package: ally core plugin
@copyright: 2012 Sourcefabric o.p.s.
@license: http://www.gnu.org/licenses/gpl-3.0.txt
@author: Gabriel Nistor

Provides the setup for creating the registry for plugins.
'''

from ..ally_core.resource_manager import resourcesManager
from ally.container import ioc
import ally_deploy_plugin as plugin

# --------------------------------------------------------------------

@ioc.start
def registerResourcesManager():
    plugin.resourcesManager = resourcesManager()
