'''
Created on Jan 21, 2013

@package: security RBAC
@copyright: 2012 Sourcefabric o.p.s.
@license: http://www.gnu.org/licenses/gpl-3.0.txt
@author: Gabriel Nistor

Contains the setups for populating default data.
'''

from ally.container import support, app, ioc
from ally.internationalization import NC_
from security.rbac.api.rbac import IRoleService, Role, QRole

# --------------------------------------------------------------------

NAME_ROOT = NC_('security role', 'ROOT')  # The name for the root role

# --------------------------------------------------------------------

@ioc.entity
def rootRoleId():
    roleService = support.entityFor(IRoleService)
    assert isinstance(roleService, IRoleService)
    return roleService.getByName(NAME_ROOT).Id

@app.populate(priority=app.PRIORITY_FIRST)
def populateRootRole():
    roleService = support.entityFor(IRoleService)
    assert isinstance(roleService, IRoleService)

    roles = roleService.getAll(limit=1, q=QRole(name=NAME_ROOT))
    if not roles:
        rootRole = Role()
        rootRole.Name = NAME_ROOT
        rootRole.Description = NC_('security role', 'Default role that provides access to all available roles and rights')
        roleService.insert(rootRole)
