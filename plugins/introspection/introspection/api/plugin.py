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
from ally.api.type import IterPart

# --------------------------------------------------------------------

@modelDevel(id='Id')
class Plugin:
    '''
    Provides the component data.
    '''
    Id = str
    Name = str
    Group = str
    Version = str
    Locale = str
    Description = str
    Loaded = bool
    Path = str
    InEgg = bool

# --------------------------------------------------------------------

@service
class IPluginService:
    '''
    Provides services for ally plugins.
    '''

    @call
    def getById(self, id:Plugin.Id) -> Plugin:
        '''
        Provides the plugin based on the provided id.
        '''

    @call
    def getPlugins(self, offset:int=None, limit:int=None) -> IterPart(Plugin):
        '''
        Provides all the plugins.
        '''
