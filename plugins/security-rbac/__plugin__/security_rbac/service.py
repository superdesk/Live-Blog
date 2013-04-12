'''
Created on Jan 21, 2013

@package: security RBAC
@copyright: 2012 Sourcefabric o.p.s.
@license: http://www.gnu.org/licenses/gpl-3.0.txt
@author: Gabriel Nistor

Contains the service setups.
'''

from ..security.service import binders
from .populate import NAME_ROOT
from ally.container import support, ioc
from ally.container.bind import intercept
from ally.container.impl.proxy import IProxyHandler
from security.api.right import IRightService
from security.rbac.api.rbac import IRoleService
from security.rbac.core.impl.proxy_assign import AssignRoleToRigh
from ally.support.util import ref

# --------------------------------------------------------------------

@ioc.entity
def proxyAssignRoleToRigh() -> IProxyHandler:
    b = AssignRoleToRigh()
    b.roleService = support.entityFor(IRoleService)
    b.roleName = NAME_ROOT
    return b

# Here we actually add a listener to the insert method of the IRightService to assign all created rights to the root role.
@ioc.before(binders)
def updateBindersForAssignToRole():
    binders().append(intercept(ref(IRightService).insert, handlers=proxyAssignRoleToRigh))

# --------------------------------------------------------------------
