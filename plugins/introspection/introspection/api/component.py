'''
Created on Mar 4, 2012

@package: introspection
@copyright: 2011 Sourcefabric o.p.s.
@license: http://www.gnu.org/licenses/gpl-3.0.txt
@author: Gabriel Nistor

Provides the components introspection.
'''

from . import modelDevel
from ally.api.config import service, call
from ally.api.type import IdString, IterPart

# --------------------------------------------------------------------

@modelDevel
class Component:
    '''
    Provides the component data.
    '''
    Id = IdString
    Name = str
    Group = str
    Version = str
    Description = str
    Loaded = bool
    Path = str
    InEgg = bool
    
# --------------------------------------------------------------------

@service
class IComponentService:
    '''
    Provides services for ally components.
    '''
    
    @call
    def getById(self, id:Component.Id) -> Component:
        '''
        Provides the component based on the provided id.
        '''
    
    @call
    def getComponents(self, offset:int=None, limit:int=None) -> IterPart(Component):
        '''
        Provides all the components.
        '''
