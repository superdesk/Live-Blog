'''
Created on May 21, 2013

@package: content article
@copyright: 2013 Sourcefabric o.p.s.
@license: http://www.gnu.org/licenses/gpl-3.0.txt
@author: Martin Saturka

Contains the SQL alchemy implementation for output target type API.
'''

from ..api.target_type import ITargetTypeService
from ..meta.target_type import TargetTypeMapped
from ally.container.ioc import injected
from ally.container.support import setup
from sql_alchemy.impl.keyed import EntityGetServiceAlchemy, \
    EntityFindServiceAlchemy

# --------------------------------------------------------------------

@injected
@setup(ITargetTypeService, name='targetTypeService')
class TargetTypeServiceAlchemy(EntityGetServiceAlchemy, EntityFindServiceAlchemy, ITargetTypeService):
    '''
    Implementation for @see: ITargetTypeService
    '''

    def __init__(self):
        '''
        Construct the output target type service.
        '''
        EntityGetServiceAlchemy.__init__(self, TargetTypeMapped)
