'''
Created on Jan 9, 2012

@package: Newscoop
@copyright: 2011 Sourcefabric o.p.s.
@license: http://www.gnu.org/licenses/gpl-3.0.txt
@author: Gabriel Nistor

Special module that is targeted by the application loader in order to deploy the components in the current system path.
'''

from ally.support.util_sys import isPackage
from package_extender import PACKAGE_EXTENDER
import os
import re
import sys
import traceback

# --------------------------------------------------------------------

configurationsFilePath = 'plugins.properties'
# The name of the configuration file

context = None
# The context of the setups.
assembly = None
# The deployed assembly.

# --------------------------------------------------------------------

resourcesManager = None
# The resource manager used to register the plugin services.

services = []
# The services to be registered after the plugin setup is finalized.

# --------------------------------------------------------------------

def deploy():
    PACKAGE_EXTENDER.addFreezedPackage('__plugin__.')
    from ally.api.configure import serviceFor
    from ally.api.operator import Service
    from ally.container import aop
    from ally.container._impl.ioc_setup import Context
    from ally.container.ioc import ConfigError, SetupError
    from ally.container.config import load, save
    from ally.core.spec.resources import ResourcesManager

    global context, assembly
    if context: raise ImportError('The plugins are already deployed')
    try:
        ctx = context = Context()
        
        for module in aop.modulesIn('__plugin__.**').load().asList():
            if not isPackage(module) and re.match('__plugin__\\.[^\\.]+$', module.__name__):
                raise SetupError('The plugin setup module %r is not allowed directly in the __plugin__ package it needs '
                                 'to be in a sub package' % module.__name__)
            ctx.addSetupModule(module)
        
        isConfig = os.path.isfile(configurationsFilePath)
        if isConfig:
            with open(configurationsFilePath, 'r') as f: config = load(f)
        else: config = {}
            
        ass = assembly = ctx.assemble(config)
        
        try: ass.processStart()
        except ConfigError:
            # We save the file in case there are missing configuration
            isConfig = False
            raise
        finally:
            if not isConfig:
                with open(configurationsFilePath, 'w') as f: save(ass.trimmedConfigurations(), f)
        
        assert isinstance(resourcesManager, ResourcesManager), 'There is no resource manager for the services'
        for service in services:
            serv = serviceFor(service)
            if not isinstance(serv, Service): raise SetupError('Invalid service instance %s' % service)
            resourcesManager.register(serv, service)
    except:
        print('-' * 150, file=sys.stderr)
        print('A problem occurred while deploying plugins', file=sys.stderr)
        traceback.print_exc()
        print('-' * 150, file=sys.stderr)
