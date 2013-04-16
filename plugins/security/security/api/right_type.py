'''
Created on Jan 14, 2013

@package: security
@copyright: 2012 Sourcefabric o.p.s.
@license: http://www.gnu.org/licenses/gpl-3.0.txt
@author: Gabriel Nistor

API specifications for security right type.
'''

from .domain_security import modelSecurity
from ally.api.config import service, call
from ally.support.api.entity import Entity, IEntityNQService

# --------------------------------------------------------------------

@modelSecurity
class RightType(Entity):
    '''
    Provides the right type data.
    '''
    Name = str
    Description = str

# --------------------------------------------------------------------

# No query

# --------------------------------------------------------------------

@service((Entity, RightType))
class IRightTypeService(IEntityNQService):
    '''
    Right type model service interface
    '''
    
    @call
    def getByName(self, name:RightType.Name) -> RightType:
        '''
        Provides the right type based on a provided name.
        '''

# --------------------------------------------------------------------
