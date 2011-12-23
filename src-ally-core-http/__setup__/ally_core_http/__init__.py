'''
Created on Jul 15, 2011

@package Newscoop
@copyright 2011 Sourcefabric o.p.s.
@license http://www.gnu.org/licenses/gpl-3.0.txt
@author: Gabriel Nistor

Contains setup and configuration files for the REST server.
'''

from ally import ioc

# --------------------------------------------------------------------
# The default configurations

serverType = ioc.config(lambda:'basic', 'The type of the server to use one of basic, cherrypy')

serverRoot = ioc.config(lambda:'resources', 'The root URL for the rest server ex: rest/resources')

serverPort = ioc.config(lambda:80, 'The port on which the server will run')

serverVersion = ioc.config(lambda:'AllyREST/0.1', 'The server version number')