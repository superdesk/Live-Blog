'''
Created on Feb 27, 2013

@package: security - role based access control
@copyright: 2012 Sourcefabric o.p.s.
@license: http://www.gnu.org/licenses/gpl-3.0.txt
@author: Gabriel Nistor

SQL Alchemy based implementation for the rbac support API.
'''

from ..spec import IRbacSupport
from ally.container import wire
from ally.container.ioc import injected
from ally.container.support import setup
from ally.support.sqlalchemy.session import SessionSupport
from security.meta.right import RightMapped
from security.meta.right_type import RightTypeMapped
from security.rbac.core.spec import IRbacService

# --------------------------------------------------------------------

@injected
@setup(IRbacSupport, name='rbacSupport')
class RbacSupportAlchemy(SessionSupport, IRbacSupport):
    '''
    Implementation for @see: IRbacSupport
    '''
    
    rbacService = IRbacService; wire.entity('rbacService')
    # Rbac service to use for complex role operations.
    
    def __init__(self):
        assert isinstance(self.rbacService, IRbacService), 'Invalid rbac service %s' % self.rbacService
    
    def iterateTypeAndRightsNames(self, rbacId):
        '''
        @see: IRbacSupport.iterateTypeAndRightsNames
        '''
        sql = self.session().query(RightMapped.Name, RightTypeMapped.Name).join(RightTypeMapped)
        sql = self.rbacService.rightsForRbacSQL(rbacId, sql=sql)
        sql = sql.order_by(RightTypeMapped.Name, RightMapped.Name)
        
        current = names = None
        for name, typeName in sql.all():
            if current != typeName:
                if current is not None: yield current, names
                current = typeName
                names = []
            names.append(name)
        if current is not None: yield current, names
            
