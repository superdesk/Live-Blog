'''
Created on Jul 15, 2011

@package Newscoop
@copyright 2011 Sourcefabric o.p.s.
@license http://www.gnu.org/licenses/gpl-3.0.txt
@author: Gabriel Nistor

Contains setup and configuration files for the HTTP REST server.
'''

from ally.container import ioc

# --------------------------------------------------------------------
# The default configurations

@ioc.config
def server_type() -> str:
    '''The type of the server to use one of basic, cherrypy'''
    return 'basic'

@ioc.config
def server_root() -> str:
    '''The root URL for the rest server ex: rest/resources'''
    return 'resources'

@ioc.config
def server_port() -> int:
    '''The port on which the server will run'''
    return 80

@ioc.config
def server_version() -> str:
    '''The server version number'''
    return 'AllyREST/0.1'
