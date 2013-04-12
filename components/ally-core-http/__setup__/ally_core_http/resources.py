'''
Created on Jun 1, 2012

@package: ally core http
@copyright: 2012 Sourcefabric o.p.s.
@license: http://www.gnu.org/licenses/gpl-3.0.txt
@author: Gabriel Nistor

Provides the configurations for the resources.
'''

from ..ally_core.resources import resourcesRoot
from ally.api.config import GET
from ally.api.type import List, TypeClass
from ally.container import ioc
from ally.core.impl.invoker import InvokerFunction
from ally.core.spec.resources import Path, InvokerInfo
from ally.support.core.util_resources import findGetAllAccessible, nodeLongName
from functools import partial

# --------------------------------------------------------------------


def rootPaths(pathOrNode):
    '''
    Provides the root paths.
    '''
    paths = findGetAllAccessible(pathOrNode)
    paths.sort(key=lambda path: nodeLongName(path.node))
    return paths

# --------------------------------------------------------------------

@ioc.after(resourcesRoot)
def decorateRoot():
    resourcesRoot().get = InvokerFunction(GET, partial(rootPaths, resourcesRoot()), List(TypeClass(Path)),
                                          [], {}, 'accessible', InvokerInfo('accessible', '.', 0, ''))
