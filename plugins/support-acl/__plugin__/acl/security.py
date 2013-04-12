'''
Created on Mar 6, 2013

@package: support acl
@copyright: 2012 Sourcefabric o.p.s.
@license: http://www.gnu.org/licenses/gpl-3.0.txt
@author: Gabriel Nistor

Provides the acl security support setup.
'''

from acl.spec import RightAcl, TypeAcl
from ally.container import support
import logging

# --------------------------------------------------------------------

log = logging.getLogger(__name__)

# --------------------------------------------------------------------

try: from .. import security
except ImportError: log.info('No security plugin available, thus no support available for it')
else:
    security = security  # Just to avoid the import warning
    # ----------------------------------------------------------------
    
    from acl.core.impl.synchronizer import SynchronizerRights
    from security.api.right import IRightService
    
    support.createEntitySetup(SynchronizerRights)
    
    # ----------------------------------------------------------------
    
    def rightId(aclRight):
        '''
        Provides the security right id for the provided acl right.
        
        @param aclRight: RightAcl
            The acl right to provide the id for.
        @return: integer
            The id of the security right.
        '''
        assert isinstance(aclRight, RightAcl), 'Invalid right %s' % aclRight
        assert isinstance(aclRight.type, TypeAcl), 'Invalid right %s, has no type' % aclRight
        
        rightService = support.entityFor(IRightService)
        assert isinstance(rightService, IRightService)
        
        return rightService.getByName(aclRight.type.name, aclRight.name).Id
