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

__all__ = ['server_basic', 'support_php', 'support_ajax']
# The default setup modules to be included.

try:
    import cherrypy
    __all__.append('server_cherrypy')
except ImportError: pass

# --------------------------------------------------------------------
# The default configurations

ioc.config(applicationMode='devel')
ioc.config(serverType='basic')
ioc.config(ajaxCrossDomain=False)
ioc.config(phpZendSupport=False)
