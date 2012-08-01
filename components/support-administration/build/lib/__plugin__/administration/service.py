'''
Created on Jan 9, 2012

@@package: ally core administration
@copyright: 2012 Sourcefabric o.p.s.
@license: http://www.gnu.org/licenses/gpl-3.0.txt
@author: Gabriel Nistor

Contains the services for the administration support.
'''

from admin.introspection.api.component import IComponentService
from admin.introspection.api.plugin import IPluginService
from ally.container import ioc
from ally.container.support import entityFor

# --------------------------------------------------------------------

@ioc.entity
def componentService() -> IComponentService:
    import ally_deploy_application
    return entityFor(IComponentService, ally_deploy_application.assembly)

@ioc.entity
def pluginService() -> IPluginService:
    import ally_deploy_application
    return entityFor(IPluginService, ally_deploy_application.assembly)
