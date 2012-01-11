'''
Created on Jan 9, 2012

@package: Newscoop
@copyright: 2011 Sourcefabric o.p.s.
@license: http://www.gnu.org/licenses/gpl-3.0.txt
@author: Gabriel Nistor

Special module that is targeted by the application loader in order to deploy the components in the current system path.
'''

from ally.container import ioc, aop
import sys
import traceback
from ally.core.spec.resources import ResourcesManager
from ally.container.config import load, save
import os
import ally_deploy_application

# --------------------------------------------------------------------

FILE_CONFIG = 'plugins.properties'
# The name of the configuration file

context = None
# The context of the setups.
assembly = None
# The deployed assembly.


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
        
        rscMng = '__setup__.ally_core.resource_manager.resourcesManager'
        ctx.addSetup(ioc.SetupEntityFixed(rscMng, ally_deploy_application.assembly.processForName(rscMng),
                                          ResourcesManager))
            
        ass = assembly = ctx.assemble(config)
        
        if not isConfig:
            with open(FILE_CONFIG, 'w') as f: save(ass.trimmedConfigurations(), f)
        
        try: ass.processStart()
        except ioc.ConfigError:
            # We save the file in case there are missing configuration
            with open(FILE_CONFIG, 'w') as f: save(ass.trimmedConfigurations(), f)
            raise
    except:
        print('-' * 150, file=sys.stderr)
        print('A problem occurred while deploying plugins', file=sys.stderr)
        traceback.print_exc()
        print('-' * 150, file=sys.stderr)
