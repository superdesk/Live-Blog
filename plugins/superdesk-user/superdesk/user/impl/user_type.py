'''
Created on May 27, 2013

@package: superdesk user
@copyright: 2013 Sourcefabric o.p.s.
@license: http://www.gnu.org/licenses/gpl-3.0.txt
@author: Martin Saturka

Contains the SQL alchemy implementation for user type API.
'''

from ..api.user_type import IUserTypeService
from ..meta.user_type import UserTypeMapped
from ally.container.ioc import injected
from ally.container.support import setup
from sql_alchemy.impl.keyed import EntityGetServiceAlchemy, EntityFindServiceAlchemy

# --------------------------------------------------------------------

@injected
@setup(IUserTypeService, name='userTypeService')
class UserTypeServiceAlchemy(EntityGetServiceAlchemy, EntityFindServiceAlchemy, IUserTypeService):
    '''
    Implementation for @see: IUserTypeService
    '''

    def __init__(self):
        '''
        Construct the user type service.
        '''
        EntityGetServiceAlchemy.__init__(self, UserTypeMapped)
