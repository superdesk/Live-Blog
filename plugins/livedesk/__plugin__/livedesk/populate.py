'''
Created on Jan 26, 2013

@package: livedesk
@copyright: 2012 Sourcefabric o.p.s.
@license: http://www.gnu.org/licenses/gpl-3.0.txt
@author: Gabriel Nistor

Contains the default data for the live desk plugin.
'''

from ally.container import support, ioc, app
from ally.internationalization import NC_
from security.api.right import IRightService, Right, QRight
from security.rbac.api.rbac import QRole, Role
from superdesk.security.api.user_rbac import IUserRbacService
from superdesk.user.api.user import IUserService, User, QUser
import hashlib
from security.rbac.api.role import IRoleService

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

@ioc.entity
def blogRoleEditorId():
    roleService = support.entityFor(IRoleService)
    assert isinstance(roleService, IRoleService)

    roles = roleService.getAll(limit=1, q=QRole(name='Editor'))
    try: editor = next(iter(roles))
    except StopIteration:
        editor = Role()
        editor.Name = NC_('security role', 'Editor')
        editor.Description = NC_('security role', 'Role that allows editor stuff')
        return roleService.insert(editor)
    return editor.Id


# --------------------------------------------------------------------

# TODO: uncomment and fix
# @app.populate
# def populateEditorRole():
#     roleService = support.entityFor(IRoleService)
#     assert isinstance(roleService, IRoleService)
#     roleService.assignRight(blogRoleEditorId(), rightId(rightLivedeskView()))
#     roleService.assignRight(blogRoleEditorId(), rightId(rightManageOwnPost()))
#     roleService.assignRight(blogRoleEditorId(), rightId(rightMediaArchiveView()))
#     roleService.assignRight(blogRoleEditorId(), rightId(rightMediaArchiveUpload()))
#     roleService.assignRight(blogRoleEditorId(), rightId(rightManageOwnPost()))
#     roleService.assignRight(blogRoleEditorId(), rightId(rightLivedeskUpdate()))
#     roleService.assignRight(blogRoleEditorId(), rightId(rightUserView()))
#     roleService.assignRole(blogRoleAdministratorId(), blogRoleEditorId())
#
# @app.populate
# def populateCollaboratorRole():
#     roleService = support.entityFor(IRoleService)
#     assert isinstance(roleService, IRoleService)
#     roleService.assignRight(blogRoleCollaboratorId(), rightId(rightLivedeskView()))
#     roleService.assignRight(blogRoleCollaboratorId(), rightId(rightManageOwnPost()))
#     roleService.assignRight(blogRoleCollaboratorId(), rightId(rightMediaArchiveView()))
#     roleService.assignRight(blogRoleCollaboratorId(), rightId(rightMediaArchiveUpload()))
#     roleService.assignRole(blogRoleAdministratorId(), blogRoleCollaboratorId())
#
# @app.populate
# def populateBlogAdministratorRole():
#     roleService = support.entityFor(IRoleService)
#     assert isinstance(roleService, IRoleService)
#     rightService = support.entityFor(IRightService)
#     assert isinstance(rightService, IRightService)
#     for right in rightService.getAll():
#         assert isinstance(right, Right)
#         if right.Name == rightRequestsInspection().name: continue
#         roleService.assignRight(blogRoleAdministratorId(), right.Id)
#     roleService.assignRole(rootRoleId(), blogRoleAdministratorId())
#     q = QRight()
#     q.name = rightRequestsInspection().name
#     for right in rightService.getAll(q=q):
#         assert isinstance(right, Right)
#         roleService.assignRight(rootRoleId(), right.Id)
#
# # --------------------------------------------------------------------

@app.populate
def populateDefaultUsers():
    userService = support.entityFor(IUserService)
    assert isinstance(userService, IUserService)
    userRbacService = support.entityFor(IUserRbacService)
    assert isinstance(userRbacService, IUserRbacService)

    for name in (('Janet', 'Admin'), ('Diane', 'Editor'), ('Andrew', 'Reporter'), ('Christine', 'Journalist')):
        loginName = name[1].lower()
        users = userService.getAll(limit=1, q=QUser(name=loginName))
        try: user = next(iter(users))
        except StopIteration:
            user = User()
            user.FirstName = name[0]
            user.LastName = name[1]
            user.EMail = '%s.%s@email.addr' % name
            user.Name = loginName
            user.Type = 'standard'
            user.Password = hashlib.sha512(b'a').hexdigest()
            user.Id = userService.insert(user)
            if user.Name == 'admin':
                userRbacService.addRole(user.Id, 'Admin')
                
# TODO: uncomment when fixed
#         if user.Name == 'admin':
#             userRbacService.assignRole(user.Id, blogRoleAdministratorId())
#         elif user.Name == 'editor':
#             userRbacService.assignRole(user.Id, blogRoleEditorId())
#         else:
#             userRbacService.assignRole(user.Id, blogRoleCollaboratorId())
