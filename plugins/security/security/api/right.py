'''
Created on Dec 21, 2012

@package: security
@copyright: 2012 Sourcefabric o.p.s.
@license: http://www.gnu.org/licenses/gpl-3.0.txt
@author: Gabriel Nistor

API specifications for security right.
'''

from .domain_security import modelSecurity
from .right_type import RightType
from ally.api.config import query, service, call
from ally.api.criteria import AsLikeOrdered
from ally.api.type import Iter
from ally.support.api.entity import Entity, QEntity, IEntityGetService, \
    IEntityCRUDService

# --------------------------------------------------------------------

@modelSecurity
class Right(Entity):
    '''
    Provides the right data.
    '''
    Type = RightType
    Name = str
    Description = str

# --------------------------------------------------------------------

@query(Right)
class QRight(QEntity):
    '''
    Query for right service
    '''
    name = AsLikeOrdered

# --------------------------------------------------------------------

@service((Entity, Right))
class IRightService(IEntityGetService, IEntityCRUDService):
    '''
    Right model service API.
    '''
    
    @call
    def getAll(self, typeId:RightType=None, offset:int=None, limit:int=None, detailed:bool=True, \
               q:QRight=None) -> Iter(Right):
        '''
        Provides the rights searched by the provided query.
        '''

# --------------------------------------------------------------------
