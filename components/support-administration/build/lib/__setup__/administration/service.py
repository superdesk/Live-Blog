'''
Created on Jan 9, 2012

@@package: ally core administration
@copyright: 2012 Sourcefabric o.p.s.
@license: http://www.gnu.org/licenses/gpl-3.0.txt
@author: Gabriel Nistor

Contains the services for the administration support.
'''

from ..ally_core.resource_management import services
from admin.introspection.api.component import IComponentService
from admin.introspection.api.plugin import IPluginService
from admin.introspection.impl.component import ComponentService
from admin.introspection.impl.plugin import PluginService
from ally.container import ioc

# --------------------------------------------------------------------

@ioc.config
def publish_introspection():
    '''
    If true the introspection services will be published and available, otherwise they will only be accessible inside
    the application.
    '''
    return False

@ioc.entity
def componentService() -> IComponentService: return ComponentService()

@ioc.entity
def pluginService() -> IPluginService:
    b = PluginService()
    b.componentService = componentService()
    return b

# --------------------------------------------------------------------

@ioc.before(services)
def publishServices():
    if publish_introspection():
        services().append(componentService())
        services().append(pluginService())
