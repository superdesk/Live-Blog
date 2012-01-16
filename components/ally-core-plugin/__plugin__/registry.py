'''
Created on Jan 12, 2012

@package Newscoop
@copyright 2011 Sourcefabric o.p.s.
@license http://www.gnu.org/licenses/gpl-3.0.txt
@author: Gabriel Nistor

Provides the setup registry for the plugins.
'''

from ally.container import ioc, support
import ally_deploy_plugin as plugin
import logging

# --------------------------------------------------------------------

FORMATTER_REST = lambda group, clazz: group + '.REST.' + clazz.__name__
# Used in formatting the rest services names.

log = logging.getLogger(__name__)

# --------------------------------------------------------------------

@ioc.entity
def services():
    '''
    The plugins services that will be registered automatically.
    '''
    return []

@ioc.before(services)
def updateServices():
    '''
    Automatically updates the services with all the setup name that use the rest service formatter.
    '''
    services().extend(support.entities().filter('**.REST.*').load().asList())

@ioc.start
def register():
    assert log.debug('Registered REST services:\n\t%s', '\n\t'.join(str(srv) for srv in services())) or True
    plugin.services = services()
