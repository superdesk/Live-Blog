'''
Created on Jan 9, 2012

@package: ally core plugin
@copyright: 2012 Sourcefabric o.p.s.
@license: http://www.gnu.org/licenses/gpl-3.0.txt
@author: Gabriel Nistor

Special module that is targeted by the application loader in order to deploy the components in the current system path.
'''

from ally.container import aop, ioc
from ally.container.config import load, save
from ally.container.ioc import ConfigError, SetupError
from ally.container.support import entityFor
from ally.core.spec.resources import IResourcesRegister
from ally.support.util_sys import isPackage
from package_extender import PACKAGE_EXTENDER
import logging
import os
import re
import sys

# --------------------------------------------------------------------

log = logging.getLogger(__name__)

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

@ioc.start
def deploy():
    if os.path.isdir(plugins_path()):
        for name in os.listdir(plugins_path()):
            path = os.path.join(plugins_path(), name)
            for exclude in excluded_plugins():
                if name.startswith(exclude): break
            else:
                if path not in sys.path: sys.path.append(path)

    isConfig, filePathConfig = os.path.isfile(configurations_file_path()), configurations_file_path()
    if isConfig:
        with open(filePathConfig, 'r') as f: config = load(f)
    else: config = {}

    PACKAGE_EXTENDER.addFreezedPackage('__plugin__.')
    pluginModules = aop.modulesIn('__plugin__.**')
    for module in pluginModules.load().asList():
        if not isPackage(module) and re.match('__plugin__\\.[^\\.]+$', module.__name__):
            raise SetupError('The plugin setup module %r is not allowed directly in the __plugin__ package it needs '
                             'to be in a sub package' % module.__name__)

    assembly = ioc.open(pluginModules, config=config)
    try:
        assembly.processStart()
        from __plugin__.plugin.registry import services
        services = services()
    except (ConfigError, SetupError):
        # We save the file in case there are missing configuration
        with open(filePathConfig, 'w') as f: save(assembly.trimmedConfigurations(), f)
        isConfig = True
        raise
    finally:
        if not isConfig:
            with open(filePathConfig, 'w') as f: save(assembly.trimmedConfigurations(), f)
        ioc.deactivate()

    import ally_deploy_application
    resourcesRegister = entityFor(IResourcesRegister, ally_deploy_application.assembly)
    assert isinstance(resourcesRegister, IResourcesRegister), 'There is no resource register for the services'

    assert log.debug('Registered REST services:\n\t%s', '\n\t'.join(str(srv) for srv in services)) or True
    for service in services:
        resourcesRegister.register(service)
