'''
Created on Jan 15, 2013

@package: support acl
@copyright: 2012 Sourcefabric o.p.s.
@license: http://www.gnu.org/licenses/gpl-3.0.txt
@author: Gabriel Nistor

Provides the acl setup.
'''

from acl.right_sevice import RightService, Alternate
from acl.spec import Acl, TypeAcl
from ally.container import ioc
from ally.internationalization import NC_

# --------------------------------------------------------------------

def aclRight(name, description) -> RightService:
    ''' Create an ACL general right '''
    b = RightService(name, description)
    aclType().add(b)
    return b

def aclAlternate(forRef, theRef):
    '''
    Adds 'theRef' reference as an alternate 'forRef' reference.
        
    @param forRef: tuple(class, string)
        The call reference for which the alternate is specified.
    @param theRef: tuple(class, string)
        The call reference which is an alternative the for reference.
    '''
    alternate().add(forRef, theRef)

# --------------------------------------------------------------------

@ioc.entity
def acl() -> Acl: return Acl()
setup = ioc.before(acl)

@ioc.entity
def aclType() -> TypeAcl:
    b = TypeAcl(NC_('security', 'Access control layer'), NC_('security',
    'Right type for the basic access control layer right setups'))
    acl().add(b)
    return b

@ioc.entity
def alternate() -> Alternate: return Alternate()
setupAlternate = ioc.before(alternate)

# --------------------------------------------------------------------

