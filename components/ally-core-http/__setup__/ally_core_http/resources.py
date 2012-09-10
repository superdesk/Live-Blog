'''
Created on Jun 1, 2012

@package: ally core http
@copyright: 2012 Sourcefabric o.p.s.
@license: http://www.gnu.org/licenses/gpl-3.0.txt
@author: Gabriel Nistor

Provides the configurations for the resources.
'''

from ..ally_core.resources import resourcesRoot, resourcesLocator
from ally.api.config import GET
from ally.api.type import List, TypeClass
from ally.container import ioc
from ally.core.impl.invoker import InvokerFunction
from ally.core.spec.resources import Path

# --------------------------------------------------------------------

@ioc.after(resourcesLocator)
def decorateRoot():
    resourcesRoot().get = InvokerFunction(GET, resourcesLocator().findGetAllAccessible,
                                          List(TypeClass(Path)), [], {})
