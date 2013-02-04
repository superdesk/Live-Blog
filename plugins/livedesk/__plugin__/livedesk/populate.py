'''
Created on Jan 26, 2013

@package: livedesk
@copyright: 2012 Sourcefabric o.p.s.
@license: http://www.gnu.org/licenses/gpl-3.0.txt
@author: Gabriel Nistor

Contains the default data for the live desk plugin.
'''

from ..gui_security.acl import aclType
from ..livedesk.actions import rightLivedeskView, rightManageOwnPost
from ..security_rbac.populate import rootRoleId
from ally.container import support, ioc
from ally.internationalization import NC_
from distribution.container import app
from security.api.right import IRightService
from security.rbac.api.rbac import IRoleService, QRole, Role
from superdesk.security.api.user_rbac import IUserRbacService
from superdesk.user.api.user import IUserService, User, QUser
import hashlib
from __plugin__.media_archive.actions import rightMediaArchiveView

# --------------------------------------------------------------------

@ioc.entity
def blogRoleAdministratorId():
    roleService = support.entityFor(IRoleService)
    assert isinstance(roleService, IRoleService)

    roles = roleService.getAll(limit=1, q=QRole(name='Administrator'))
    try: admin = next(iter(roles))
    except StopIteration:
        admin = Role()
        admin.Name = NC_('security role', 'Administrator')
        admin.Description = NC_('security role', 'Role that allows all rights')
        return roleService.insert(admin)
    return admin.Id

@ioc.entity
def blogRoleCollaboratorId():
    roleService = support.entityFor(IRoleService)
    assert isinstance(roleService, IRoleService)

    roles = roleService.getAll(limit=1, q=QRole(name='Collaborator'))
    try: collaborator = next(iter(roles))
    except StopIteration:
        collaborator = Role()
        collaborator.Name = NC_('security role', 'Collaborator')
        collaborator.Description = NC_('security role', 'Role that allows submit to desk and edit his own posts')
        return roleService.insert(collaborator)
    return collaborator.Id

# --------------------------------------------------------------------

@app.populate
def populateCollaboratorRole():
    roleService = support.entityFor(IRoleService)
    assert isinstance(roleService, IRoleService)
    rightService = support.entityFor(IRightService)
    assert isinstance(rightService, IRightService)
    roleService.assignRight(blogRoleCollaboratorId(), rightService.getByName(aclType().name, rightLivedeskView().name).Id)
    roleService.assignRight(blogRoleCollaboratorId(), rightService.getByName(aclType().name, rightManageOwnPost().name).Id)
    roleService.assignRight(blogRoleCollaboratorId(), rightService.getByName(aclType().name, rightMediaArchiveView().name).Id)
    roleService.assignRole(rootRoleId(), blogRoleCollaboratorId())

@app.populate
def populateBlogAdministratorRole():
    roleService = support.entityFor(IRoleService)
    assert isinstance(roleService, IRoleService)
    rightService = support.entityFor(IRightService)
    assert isinstance(rightService, IRightService)
    roleService.assignRole(rootRoleId(), blogRoleAdministratorId())

# --------------------------------------------------------------------

@app.populate
def populateDefaultUsers():
    userService = support.entityFor(IUserService)
    assert isinstance(userService, IUserService)
    userRbacService = support.entityFor(IUserRbacService)
    assert isinstance(userRbacService, IUserRbacService)

    users = userService.getAll(limit=1, q=QUser(name='admin'))
    if not users:
        user = User()
        user.FirstName = 'Change admin'
        user.LastName = 'name'
        user.EMail = 'admin@change.mail'
        user.Name = 'admin'
        user.Password = hashlib.sha512(b'a').hexdigest()
        user.Id = userService.insert(user)
    else: user = next(iter(users))
    userRbacService.assignRole(user.Id, blogRoleAdministratorId())

    for name in ('collab1', 'collab2'):
        users = userService.getAll(limit=1, q=QUser(name=name))
        if not users:
            user = User()
            user.FirstName = 'Change ' + name
            user.LastName = 'name'
            user.EMail = name + '@change.mail'
            user.Name = name
            user.Password = hashlib.sha512(b'a').hexdigest()
            user.Id = userService.insert(user)
        else: user = next(iter(users))
        userRbacService.assignRole(user.Id, blogRoleCollaboratorId())
