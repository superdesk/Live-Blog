'''
Created on Jan 19, 2012

@package ally core plugins
@copyright 2011 Sourcefabric o.p.s.
@license http://www.gnu.org/licenses/gpl-3.0.txt
@author: Gabriel Nistor

API specifications for plugin support.
'''

from ally.api.config import model, service, call
from ally.api.type import IdString, Iter

#TODO: add reloading and auto reloading for plugins. 
# --------------------------------------------------------------------

@model
class Plugin:
    '''
    Provides the plugin data.
    '''
    Name = IdString
    Location = str
    Description = str
    
# --------------------------------------------------------------------

@service
class IPluginService:
    '''
    Provides services for plugins.
    '''
    
    @call
    def getAllRegisteredPlugins(self, offset:int=None, limit:int=None) -> Iter(Plugin):
        '''
        Provides all the plugins.
        
        @param offset: integer
            The offset to retrieve the plugins from.
        @param limit: integer
            The limit of plugins to retrieve.
        '''
