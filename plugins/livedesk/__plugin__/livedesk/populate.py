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
from __plugin__.media_archive.actions import rightMediaArchiveUpload
from __plugin__.livedesk.actions import rightLivedeskUpdate
from __plugin__.superdesk_user.actions import rightUserView
from superdesk.general_setting.api.general_setting import IGeneralSettingService,\
    GeneralSetting
from superdesk.general_setting.meta.general_setting import GeneralSettingMapped
from sqlalchemy.orm.session import Session
from ..superdesk.db_superdesk import alchemySessionCreator

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

@app.populate
def populateEditorRole():
    roleService = support.entityFor(IRoleService)
    assert isinstance(roleService, IRoleService)
    roleService.assignRight(blogRoleEditorId(), rightId(rightLivedeskView()))
    roleService.assignRight(blogRoleEditorId(), rightId(rightManageOwnPost()))
    roleService.assignRight(blogRoleEditorId(), rightId(rightMediaArchiveView()))
    roleService.assignRight(blogRoleEditorId(), rightId(rightMediaArchiveUpload()))
    roleService.assignRight(blogRoleEditorId(), rightId(rightManageOwnPost()))
    roleService.assignRight(blogRoleEditorId(), rightId(rightLivedeskUpdate()))
    roleService.assignRight(blogRoleEditorId(), rightId(rightUserView()))
    roleService.assignRole(blogRoleAdministratorId(), blogRoleEditorId())

@app.populate
def populateCollaboratorRole():
    roleService = support.entityFor(IRoleService)
    assert isinstance(roleService, IRoleService)
    roleService.assignRight(blogRoleCollaboratorId(), rightId(rightLivedeskView()))
    roleService.assignRight(blogRoleCollaboratorId(), rightId(rightManageOwnPost()))
    roleService.assignRight(blogRoleCollaboratorId(), rightId(rightMediaArchiveView()))
    roleService.assignRight(blogRoleCollaboratorId(), rightId(rightMediaArchiveUpload()))
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

    for name in (('Janet', 'Admin'), ('Diane', 'Editor'), ('Andrew', 'Reporter'), ('Christine', 'Journalist')):
        loginName = name[1].lower()
        users = userService.getAll(limit=1, q=QUser(name=loginName))
        if not users:
            user = User()
            user.FirstName = name[0]
            user.LastName = name[1]
            user.EMail = '%s.%s@email.addr' % name
            user.Name = loginName
            user.Password = hashlib.sha512(b'a').hexdigest()
            user.Id = userService.insert(user)
        else: user = next(iter(users))
        if user.Name == 'admin':
            userRbacService.assignRole(user.Id, blogRoleAdministratorId())
        elif user.Name == 'editor':
            userRbacService.assignRole(user.Id, blogRoleEditorId())
        else:
            userRbacService.assignRole(user.Id, blogRoleCollaboratorId())
            
@app.populate
def populateVersionConfig():    
    creator = alchemySessionCreator()
    session = creator()
    assert isinstance(session, Session)
    
    generalSettingService = support.entityFor(IGeneralSettingService)
    assert isinstance(generalSettingService, IGeneralSettingService)    
    
    generalSetting = GeneralSetting()
    generalSetting.Group = 'version'
    
    
    if session.query(GeneralSettingMapped).filter(GeneralSettingMapped.Key == 'major').count() == 0:
        generalSetting.Key = 'major'
        generalSetting.Value = '1'
        generalSettingService.insert(generalSetting)  
    
    if session.query(GeneralSettingMapped).filter(GeneralSettingMapped.Key == 'minor').count() == 0:
        generalSetting.Key = 'minor'
        generalSetting.Value = '6'
        generalSettingService.insert(generalSetting) 
    
    if session.query(GeneralSettingMapped).filter(GeneralSettingMapped.Key == 'revision').count() == 0:
        generalSetting.Key = 'revision'
        generalSetting.Value = '0'
        generalSettingService.insert(generalSetting) 
