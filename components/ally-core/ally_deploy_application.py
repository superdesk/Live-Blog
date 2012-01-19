'''
Created on Jan 9, 2012

@package: Newscoop
@copyright: 2011 Sourcefabric o.p.s.
@license: http://www.gnu.org/licenses/gpl-3.0.txt
@author: Gabriel Nistor

Special module that is targeted by the application loader in order to deploy the components in the current system path.
'''

# --------------------------------------------------------------------

from ally.container import aop
from ally.container._impl.ioc_setup import Context, ConfigError
from ally.container.config import save, load
import os
import sys
import traceback

# --------------------------------------------------------------------

FILE_CONFIG = 'application.properties'
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
        ctx = context = Context()
        
        for module in aop.modulesIn('__setup__.**').load().asList():
            ctx.addSetupModule(module)
        
        isConfig = os.path.isfile(FILE_CONFIG)
        if isConfig:
            with open(FILE_CONFIG, 'r') as f: config = load(f)
        else: config = {}
        
        ass = assembly = ctx.assemble(config)
        
        try: ass.processStart()
        except ConfigError:
            # We save the file in case there are missing configuration
            with open(FILE_CONFIG, 'w') as f: save(ass.trimmedConfigurations(), f)
            raise
        if not isConfig:
            with open(FILE_CONFIG, 'w') as f: save(ass.trimmedConfigurations(), f)
            
    except:
        print('-' * 150, file=sys.stderr)
        print('A problem occurred while deploying', file=sys.stderr)
        traceback.print_exc()
        print('-' * 150, file=sys.stderr)
