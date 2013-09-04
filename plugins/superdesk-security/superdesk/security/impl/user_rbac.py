'''
Created on Jan 21, 2013

@package: superdesk security
@copyright 2011 Sourcefabric o.p.s.
@license http://www.gnu.org/licenses/gpl-3.0.txt
@author: Gabriel Nistor

Implementation for user RBAC.
'''

from ..meta.user_rbac import RbacUserMapped
from acl.core.spec import IAclPermissionProvider, ICompensateProvider
from ally.api.error import IdError
from ally.container import wire
from ally.container.ioc import injected
from ally.container.support import setup
from ally.support.api.util_service import emptyCollection, processCollection
from gui.action.core.spec import listRootPaths, listCompletePaths
from gui.action.meta.category_right import RightAction
from security.rbac.core.impl.rbac import RbacServiceAlchemy
from security.rbac.meta.rbac import Rbac
from sql_alchemy.support.mapper import tableFor
from sqlalchemy.orm.exc import NoResultFound
from sqlalchemy.sql.expression import insert, distinct
from superdesk.security.api.user_rbac import IUserRbacService
from superdesk.user.meta.user import UserMapped

# --------------------------------------------------------------------

@injected
@setup(IUserRbacService, name='userRbacService')
class UserRbacServiceAlchemy(RbacServiceAlchemy, IAclPermissionProvider, ICompensateProvider, IUserRbacService):
    '''
    Implementation for @see: IUserRbacService
    '''
    
    aclPermissionRightsProvider = IAclPermissionProvider; wire.entity('aclPermissionRightsProvider')
    compensateRightsProvider = ICompensateProvider; wire.entity('compensateRightsProvider')
    
    def __init__(self):
        assert isinstance(self.aclPermissionRightsProvider, IAclPermissionProvider), \
        'Invalid acl permission provider %s' % self.aclPermissionRightsProvider
        assert isinstance(self.compensateRightsProvider, ICompensateProvider), \
        'Invalid acl compensate provider %s' % self.compensateRightsProvider
        RbacServiceAlchemy.__init__(self, RbacUserMapped)
    
    def getActions(self, identifier, **options):
        '''
        @see: IUserRbacService.getActions
        '''
        rbacId = self.findRbacId(identifier)
        if rbacId is None: return emptyCollection(**options)

        sql = self.session().query(distinct(RightAction.actionPath))
        sql = sql.filter(RightAction.categoryId.in_(self.sqlRights(rbacId)))  # @UndefinedVariable

        return processCollection(listCompletePaths(path for path, in sql.all()), **options)
    
    def getActionsRoot(self, identifier, **options):
        '''
        @see: IUserRbacService.getActions
        '''
        rbacId = self.findRbacId(identifier)
        if rbacId is None: return emptyCollection(**options)

        sql = self.session().query(distinct(RightAction.actionPath))
        sql = sql.filter(RightAction.categoryId.in_(self.sqlRights(rbacId)))  # @UndefinedVariable

        return processCollection(listRootPaths(path for path, in sql.all()), **options)
        
    def getSubActions(self, identifier, parentPath, **options):
        '''
        @see: IUserRbacService.getSubActions
        '''
        assert isinstance(parentPath, str), 'Invalid parent path %s' % parentPath
        
        rbacId = self.findRbacId(identifier)
        if rbacId is None: return emptyCollection(**options)
        
        sql = self.session().query(distinct(RightAction.actionPath))
        sql = sql.filter(RightAction.categoryId.in_(self.sqlRights(rbacId)))  # @UndefinedVariable
        sql = sql.filter(RightAction.actionPath.like('%s.%%' % parentPath))  # @UndefinedVariable
        
        return processCollection(listRootPaths((path for path, in sql.all()), len(parentPath) + 1), **options)
    
    # ----------------------------------------------------------------
    
    def obtainRbacId(self, identifier):
        '''
        @see: RbacServiceAlchemy.obtainRbacId
        '''
        assert isinstance(identifier, int), 'Invalid user id %s' % identifier
        sql = self.session().query(RbacUserMapped.rbacId)
        sql = sql.filter(RbacUserMapped.userId == identifier)
        try: rbacUserId, = sql.one()
        except NoResultFound:
            sql = self.session().query(UserMapped.userId)
            sql = sql.filter(UserMapped.userId == identifier)
            if not sql.count(): raise IdError(UserMapped)
            
            rbac = Rbac()
            self.session().add(rbac)
            self.session().flush((rbac,))
            rbacUserId = rbac.id
            self.session().execute(insert(tableFor(RbacUserMapped), {RbacUserMapped.userId: identifier,
                                                                     RbacUserMapped.rbacId: rbacUserId}))
            
        return rbacUserId

    # ----------------------------------------------------------------
    
    def iteratePermissions(self, acl):
        '''
        @see: IAclPermissionProvider.iteratePermissions
        '''
        rbacId = self.findRbacId(acl)
        if rbacId is None: return ()
        return self.aclPermissionRightsProvider.iteratePermissions(self.sqlRights(rbacId))
    
    # ----------------------------------------------------------------
    
    def iterateCompensates(self, acl):
        '''
        @see: ICompensateProvider.iterateCompensates
        '''
        rbacId = self.findRbacId(acl)
        if rbacId is None: return ()
        return self.compensateRightsProvider.iterateCompensates(self.sqlRights(rbacId))
    
