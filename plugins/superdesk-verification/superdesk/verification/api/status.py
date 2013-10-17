'''
Created on Oct 4, 2013

@package: superdesk post verification
@copyright: 2013 Sourcefabric o.p.s.
@license: http://www.gnu.org/licenses/gpl-3.0.txt
@author: Ioan v. Pocol

API specifications for post verification status.
'''

from ally.api.config import service
from ally.support.api.keyed import Entity, IEntityGetService, IEntityFindService
from superdesk.api.domain_superdesk import modelData

# --------------------------------------------------------------------

@modelData
class VerificationStatus(Entity):
    '''
    Provides the post verification status model.
    '''

# --------------------------------------------------------------------

# No query

# --------------------------------------------------------------------

@service((Entity, VerificationStatus))
class IVerificationStatusService(IEntityGetService, IEntityFindService):
    '''
    Provides the service methods for the post verification status.
    '''
