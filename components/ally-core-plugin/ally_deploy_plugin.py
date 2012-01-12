'''
Created on Jan 9, 2012

@package: Newscoop
@copyright: 2011 Sourcefabric o.p.s.
@license: http://www.gnu.org/licenses/gpl-3.0.txt
@author: Gabriel Nistor

Special module that is targeted by the application loader in order to deploy the components in the current system path.
'''

from ally.api.configure import serviceFor
from ally.container import aop
from ally.container._impl import ioc
from ally.container.config import load, save
from ally.core.spec.resources import ResourcesManager
import os
import sys
import traceback

# --------------------------------------------------------------------

FILE_CONFIG = 'plugins.properties'
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
    global context, assembly
    if context: raise ImportError('The application is already deployed')
    try:
        ctx = context = ioc.Context()
        
        for module in aop.modulesIn('__plugin__.**').load().asList():
            ctx.addSetupModule(module)
        
        isConfig = os.path.isfile(FILE_CONFIG)
        if isConfig:
            with open(FILE_CONFIG, 'r') as f: config = load(f)
        else: config = {}
            
        ass = assembly = ctx.assemble(config)
        
        if not isConfig:
            with open(FILE_CONFIG, 'w') as f: save(ass.trimmedConfigurations(), f)
        
        try: ass.processStart()
        except ioc.ConfigError:
            # We save the file in case there are missing configuration
            with open(FILE_CONFIG, 'w') as f: save(ass.trimmedConfigurations(), f)
            raise
        
        assert isinstance(resourcesManager, ResourcesManager), 'There is no resource manager for the services'
        for service in services: resourcesManager.register(serviceFor(service), service)
    except:
        print('-' * 150, file=sys.stderr)
        print('A problem occurred while deploying plugins', file=sys.stderr)
        traceback.print_exc()
        print('-' * 150, file=sys.stderr)
