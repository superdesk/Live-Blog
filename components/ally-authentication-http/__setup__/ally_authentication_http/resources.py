'''
Created on Jun 1, 2012

@package: ally authentication http
@copyright: 2012 Sourcefabric o.p.s.
@license: http://www.gnu.org/licenses/gpl-3.0.txt
@author: Gabriel Nistor

Provides the configurations for the resources.
'''

from ..ally_authentication_core.resources import resourcesLocatorAuthentication, \
    resourcesRootAuthentication
from ally.api.config import GET
from ally.api.type import List, TypeClass
from ally.container import ioc
from ally.core.impl.invoker import InvokerFunction
from ally.core.spec.resources import Path

# --------------------------------------------------------------------

@ioc.after(resourcesLocatorAuthentication)
def decorateRootAuthentication():
    resourcesRootAuthentication().get = InvokerFunction(GET, resourcesLocatorAuthentication().findGetAllAccessible,
                                                        List(TypeClass(Path)), [], {})
