'''
Created on Mar 4, 2012

@package: administration introspection
@copyright: 2011 Sourcefabric o.p.s.
@license: http://www.gnu.org/licenses/gpl-3.0.txt
@author: Gabriel Nistor

Provides the plugin introspection.
'''

from ..api.component import Component
from admin.api.domain_admin import modelAdmin
from ally.api.config import service, call
from ally.api.type import Iter

# --------------------------------------------------------------------

@modelAdmin(id='Id')
class Plugin:
    '''
    Provides the plugin data.
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
    Component = Component

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
    def getPlugins(self, offset:int=None, limit:int=None) -> Iter(Plugin):
        '''
        Provides all the plugins.
        '''
