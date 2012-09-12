'''
Created on Jul 15, 2011

@package: ally core http
@copyright: 2012 Sourcefabric o.p.s.
@license: http://www.gnu.org/licenses/gpl-3.0.txt
@author: Gabriel Nistor

Contains setup and configuration files for the HTTP REST server.
'''

from ally.container import ioc
from .. import ally_api

# --------------------------------------------------------------------

NAME = 'ally core HTTP'
GROUP = ally_api.GROUP
VERSION = '1.0'
DESCRIPTION = 'Provides the HTTP communication support'

# --------------------------------------------------------------------
# The default configurations

@ioc.config
def server_type() -> str:
    '''The type of the server to use one of basic, cherrypy'''
    return 'basic'

@ioc.config
def server_port() -> int:
    '''The port on which the server will run'''
    return 8080

@ioc.config
def server_version() -> str:
    '''The server version name'''
    return 'AllyREST/0.1'

@ioc.config
def server_pattern_rest():
    ''' The pattern used for matching the REST resources paths in HTTP URL's'''
    return '^resources(/|(?=\\.)|$)'
