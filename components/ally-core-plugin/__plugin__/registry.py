'''
Created on Jan 12, 2012

@package Newscoop
@copyright 2011 Sourcefabric o.p.s.
@license http://www.gnu.org/licenses/gpl-3.0.txt
@author: Gabriel Nistor

Provides the setup registry for the plugins.
'''

from ally.container import ioc
import ally_deploy_plugin as plugin

# --------------------------------------------------------------------

@ioc.entity
def services():
    '''
    The plugins services that will be registered automatically.
    '''
    return plugin.services

@ioc.start
def register():
    # We just call the registry setups to trigger the creation.
    services()
