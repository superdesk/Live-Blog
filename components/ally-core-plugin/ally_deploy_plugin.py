'''
Created on Jan 9, 2012

@package: ally core plugin
@copyright: 2012 Sourcefabric o.p.s.
@license: http://www.gnu.org/licenses/gpl-3.0.txt
@author: Gabriel Nistor

Special module that is targeted by the application loader in order to deploy the components in the current system path.
'''

import os
import re
import sys
import traceback
import logging

# --------------------------------------------------------------------

log = logging.getLogger(__name__)

configurationsFilePath = 'plugins.properties'
# The name of the configuration file

assembly = None
# The assembly for the plugins resources

# --------------------------------------------------------------------

resourcesManager = None
# The resource manager used to register the plugin services.

services = []
# The services to be registered after the plugin setup is finalized.

# --------------------------------------------------------------------

def deploy():
    from package_extender import PACKAGE_EXTENDER
    PACKAGE_EXTENDER.addFreezedPackage('__plugin__.')
    from ally.support.util_sys import isPackage
    from ally.container import aop, ioc
    from ally.container.ioc import ConfigError, SetupError
    from ally.container.config import load, save
    from ally.core.spec.resources import ResourcesManager

    global assembly
    if assembly: raise ImportError('The plugins are already deployed')

    try:
        isConfig = os.path.isfile(configurationsFilePath)
        if isConfig:
            with open(configurationsFilePath, 'r') as f: config = load(f)
        else: config = {}

        pluginModules = aop.modulesIn('__plugin__.**')
        for module in pluginModules.load().asList():
            if not isPackage(module) and re.match('__plugin__\\.[^\\.]+$', module.__name__):
                raise SetupError('The plugin setup module %r is not allowed directly in the __plugin__ package it needs '
                                 'to be in a sub package' % module.__name__)

        assembly = ioc.open(pluginModules, config=config)
        try: assembly.processStart()
        except (ConfigError, SetupError):
            # We save the file in case there are missing configuration
            with open(configurationsFilePath, 'w') as f: save(assembly.trimmedConfigurations(), f)
            isConfig = True
            raise
        finally:
            if not isConfig:
                with open(configurationsFilePath, 'w') as f: save(assembly.trimmedConfigurations(), f)
            ioc.close()

        assert isinstance(resourcesManager, ResourcesManager), 'There is no resource manager for the services'
        assert log.debug('Registered REST services:\n\t%s', '\n\t'.join(str(srv) for srv in services)) or True
        for service in services:
            resourcesManager.register(service)
    except:
        print('-' * 150, file=sys.stderr)
        print('A problem occurred while deploying plugins', file=sys.stderr)
        traceback.print_exc()
        print('-' * 150, file=sys.stderr)
