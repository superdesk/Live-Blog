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
from ally.container.ioc import SetupError

# --------------------------------------------------------------------

@ioc.entity
def componentService() -> IComponentService:
    try: import application
    except ImportError: raise SetupError('Cannot access the application module')
    return entityFor(IComponentService, application.assembly)

@ioc.entity
def pluginService() -> IPluginService:
    try: import application
    except ImportError: raise SetupError('Cannot access the application module')
    return entityFor(IPluginService, application.assembly)
