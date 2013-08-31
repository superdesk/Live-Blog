'''
Created on May 27, 2013

@package: superdesk user
@copyright: 2013 Sourcefabric o.p.s.
@license: http://www.gnu.org/licenses/gpl-3.0.txt
@author: Martin Saturka

API specifications for user types.
'''

from ally.api.config import service
from superdesk.api.domain_superdesk import modelHR
from ally.support.api.entity import IEntityNQPrototype

# --------------------------------------------------------------------

@modelHR(id='Key')
class UserType:
    '''
    Provides the user type model.
    '''
    Key = str

# --------------------------------------------------------------------
# No query
# --------------------------------------------------------------------

@service(('Entity', UserType))
class IUserTypeService(IEntityNQPrototype):
    '''
    Provides the service methods for the user type.
    '''
