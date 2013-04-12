'''
Created on Feb 1, 2013

@package: service CDM
@copyright: 2012 Sourcefabric o.p.s.
@license: http://www.gnu.org/licenses/gpl-3.0.txt
@author: Gabriel Nistor

Provides the server configuration.
'''

from ..ally_http.server import assemblyServer, updateAssemblyServer
from .processor import assemblyContent
from ally.container import ioc
from ally.design.processor.handler import Handler
from ally.http.impl.processor.router_by_path import RoutingByPathHandler

# --------------------------------------------------------------------

@ioc.config
def server_provide_content():
    ''' Flag indicating that this server should provide content from the local configured repository path'''
    return True

@ioc.config
def server_pattern_content():
    ''' The pattern used for matching the rest content paths in HTTP URL's'''
    return '^content(?:/|(?=\\.)|$)(.*)'

# --------------------------------------------------------------------

@ioc.entity
def contentRouter() -> Handler:
    b = RoutingByPathHandler()
    b.assembly = assemblyContent()
    b.pattern = server_pattern_content()
    return b
    
@ioc.before(updateAssemblyServer)
def updateAssemblyServerForContent():
    if server_provide_content():
        assemblyServer().add(contentRouter())
