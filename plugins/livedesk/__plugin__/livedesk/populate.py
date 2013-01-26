'''
Created on Jan 26, 2013

@package: livedesk
@copyright: 2012 Sourcefabric o.p.s.
@license: http://www.gnu.org/licenses/gpl-3.0.txt
@author: Gabriel Nistor

Contains the default data for the live desk plugin.
'''

from ally.container import support, ioc
from distribution.container import app
from superdesk.security.api.user_rbac import IUserRbacService
from superdesk.user.api.user import IUserService, User, QUser
import hashlib
from security.api.right import IRightService
from ..gui_security.acl import aclType
from ..livedesk.actions import rightLivedeskView
from security.rbac.api.rbac import IRoleService, QRole, Role
from ally.internationalization import NC_

# --------------------------------------------------------------------

@ioc.entity
def blogViewerRoleId():
    roleService = support.entityFor(IRoleService)
    assert isinstance(roleService, IRoleService)
    
    roles = roleService.getAll(limit=1, q=QRole(name='Blog viewer'))
    try: viewerRole = next(iter(roles))
    except StopIteration:
        viewerRole = Role()
        viewerRole.Name = NC_('security role', 'Blog viewer')
        viewerRole.Description = NC_('security role', 'Role that allows the view only access to blogs')
        return roleService.insert(viewerRole)
    return viewerRole.Id
        
# --------------------------------------------------------------------

@app.populate
def populateBlogViewerRoleRights():
    roleService = support.entityFor(IRoleService)
    assert isinstance(roleService, IRoleService)
    rightService = support.entityFor(IRightService)
    assert isinstance(rightService, IRightService)
    roleService.assignRight(blogViewerRoleId(), rightService.getByName(aclType().name, rightLivedeskView().name).Id)

@app.populate
def populateBlogViewer():
    userService = support.entityFor(IUserService)
    assert isinstance(userService, IUserService)
    userRbacService = support.entityFor(IUserRbacService)
    assert isinstance(userRbacService, IUserRbacService)
    
    users = userService.getAll(limit=1, q=QUser(name='view'))
    if not users:
        user = User()
        user.Name = 'view'
        user.Password = hashlib.sha512(b'view').hexdigest()
        user.Id = userService.insert(user)
    else: user = next(iter(users))
    
    userRbacService.assignRole(user.Id, blogViewerRoleId())
