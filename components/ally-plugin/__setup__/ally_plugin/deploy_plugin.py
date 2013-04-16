'''
Created on Jan 9, 2012

@package: ally plugin
@copyright: 2012 Sourcefabric o.p.s.
@license: http://www.gnu.org/licenses/gpl-3.0.txt
@author: Gabriel Nistor

Special module that is targeted by the application loader in order to deploy the components in the current system path.
'''

from ally.container import aop, ioc, context, event, support
from ally.container.error import SetupError
from ally.container.impl.config import load
from ally.support.util_sys import isPackage
from package_extender import PACKAGE_EXTENDER
import logging
import os
import re
import sys

# --------------------------------------------------------------------

log = logging.getLogger(__name__)

# --------------------------------------------------------------------

def loadPlugins():
    ''' Add the plugins to the python path'''
    if os.path.isdir(plugins_path()):
        if '__plugin__' in sys.modules:
            raise ImportError('The __plugin__ module is already present in the system modules, this means that adding '
                              'plugin paths will have no effect. To correct this you need to remove from all '
                              'components setups any import that contains __plugin__!')
        for name in os.listdir(plugins_path()):
            path = os.path.join(plugins_path(), name)
            for exclude in excluded_plugins():
                if name.startswith(exclude): break
            else:
                path = os.path.abspath(path)
                if path not in sys.path: sys.path.append(path)

def openPlugins():
    ''' Add the plugins to the python path and also open the assembly for plugins'''
    loadPlugins()
    if not os.path.isfile(configurations_file_path()):
        print('The configuration file "%s" does not exist, create one by running the the application '
              'with "-dump" option' % configurations_file_path())
        sys.exit(1)
    with open(configurations_file_path(), 'r') as f: config = load(f)

    PACKAGE_EXTENDER.addFreezedPackage('__plugin__.')
    pluginModules = aop.modulesIn('__plugin__.**')
    for module in pluginModules.load().asList():
        if not isPackage(module) and re.match('__plugin__\\.[^\\.]+$', module.__name__):
            raise SetupError('The plugin setup module \'%s\' is not allowed directly in the __plugin__ package it needs '
                             'to be in a sub package' % module.__name__)

    context.open(pluginModules, config=config, included=True)

# --------------------------------------------------------------------

@ioc.config
def plugins_path():
    '''
    The path where the plugin eggs are located.
    '''
    return 'plugins'

@ioc.config
def configurations_file_path():
    '''
    The name of the configuration file for the plugins.
    '''
    return 'plugins.properties'

@ioc.config
def excluded_plugins():
    '''
    The prefix for the plugins to be excluded, something like: gui-action, introspection-request.
    '''
    return []

# --------------------------------------------------------------------

@ioc.start(priority=ioc.PRIORITY_FIRST)
def deploy():
    openPlugins()
    
    try: context.processStart()
    finally: context.deactivate()

@event.on(event.REPAIR)
def repair():
    openPlugins()
    
    try:
        for call, name, _trigger in support.eventsFor(event.REPAIR):
            log.info('Executing plugins repair event call \'%s\'', name)
            call()
    finally: context.deactivate()
