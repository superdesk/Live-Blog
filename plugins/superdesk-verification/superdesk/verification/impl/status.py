'''
Created on Oct 3, 2013

@package: superdesk post verification
@copyright: 2013 Sourcefabric o.p.s.
@license: http://www.gnu.org/licenses/gpl-3.0.txt
@author: Ioan v. Pocol

Contains the SQL alchemy implementation for post verification status API.
'''

from ..api.status import IVerificationStatusService
from ..meta.status import VerificationStatusMapped
from ally.container.ioc import injected
from ally.container.support import setup
from sql_alchemy.impl.keyed import EntityGetServiceAlchemy, \
    EntityFindServiceAlchemy

# --------------------------------------------------------------------

@injected
@setup(IVerificationStatusService, name='verificationStatusService')
class VerificationStatusServiceAlchemy(EntityGetServiceAlchemy, EntityFindServiceAlchemy, IVerificationStatusService):
    '''
    Implementation for @see: IVerificationStatusService
    '''

    def __init__(self):
        '''
        Construct the post verification status service.
        '''
        EntityGetServiceAlchemy.__init__(self, VerificationStatusMapped)
