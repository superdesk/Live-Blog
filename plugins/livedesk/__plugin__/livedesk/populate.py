'''
Created on Jan 26, 2013

@package: livedesk
@copyright: 2012 Sourcefabric o.p.s.
@license: http://www.gnu.org/licenses/gpl-3.0.txt
@author: Gabriel Nistor

Contains the default data for the live desk plugin.
'''

from ..acl.security import rightId
from ..administration.actions import rightRequestsInspection
from ..livedesk.actions import rightLivedeskView, rightManageOwnPost
from ..media_archive.actions import rightMediaArchiveView
from ..security_rbac.populate import rootRoleId
from ally.container import support, ioc, app
from ally.internationalization import NC_
from security.api.right import IRightService, Right, QRight
from security.rbac.api.rbac import IRoleService, QRole, Role
from superdesk.security.api.user_rbac import IUserRbacService
from superdesk.user.api.user import IUserService, User, QUser
import hashlib

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
    roleService.assignRight(blogRoleCollaboratorId(), rightId(rightLivedeskView()))
    roleService.assignRight(blogRoleCollaboratorId(), rightId(rightManageOwnPost()))
    roleService.assignRight(blogRoleCollaboratorId(), rightId(rightMediaArchiveView()))
    roleService.assignRole(blogRoleAdministratorId(), blogRoleCollaboratorId())

@app.populate
def populateBlogAdministratorRole():
    roleService = support.entityFor(IRoleService)
    assert isinstance(roleService, IRoleService)
    rightService = support.entityFor(IRightService)
    assert isinstance(rightService, IRightService)
    for right in rightService.getAll():
        assert isinstance(right, Right)
        if right.Name == rightRequestsInspection().name: continue
        roleService.assignRight(blogRoleAdministratorId(), right.Id)
    roleService.assignRole(rootRoleId(), blogRoleAdministratorId())
    q = QRight()
    q.name = rightRequestsInspection().name
    for right in rightService.getAll(q=q):
        assert isinstance(right, Right)
        roleService.assignRight(rootRoleId(), right.Id)

# --------------------------------------------------------------------

@app.populate
def populateDefaultUsers():
    userService = support.entityFor(IUserService)
    assert isinstance(userService, IUserService)
    userRbacService = support.entityFor(IUserRbacService)
    assert isinstance(userRbacService, IUserRbacService)

    users = userService.getAll(limit=1, q=QUser(name='Janet'))
    if not users:
        user = User()
        user.FirstName = 'Janet'
        user.LastName = 'Editor'
        user.EMail = 'Janet.Editor@email.addr'
        user.Name = 'admin'
        user.Password = hashlib.sha512(b'a').hexdigest()
        user.Id = userService.insert(user)
    else: user = next(iter(users))
    userRbacService.assignRole(user.Id, blogRoleAdministratorId())

    for name in (('Andrew', 'Reporter'), ('Christine', 'Journalist')):
        users = userService.getAll(limit=1, q=QUser(name=name[0]))
        if not users:
            user = User()
            user.FirstName = name[0]
            user.LastName = name[1]
            user.EMail = '%s.%s@email.addr' % name
            user.Name = name[1].lower()
            user.Password = hashlib.sha512(b'a').hexdigest()
            user.Id = userService.insert(user)
        else: user = next(iter(users))
        userRbacService.assignRole(user.Id, blogRoleCollaboratorId())
