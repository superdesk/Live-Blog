'''
Created on Jan 9, 2012

@package: Newscoop
@copyright: 2011 Sourcefabric o.p.s.
@license: http://www.gnu.org/licenses/gpl-3.0.txt
@author: Gabriel Nistor

Special module that is targeted by the application loader in order to deploy the components in the current system path.
'''

import ally_deploy_application as app
import sys
import traceback
from ally.core.spec.resources import ResourcesManager

# --------------------------------------------------------------------

CONTEXT = None
# The context of the plugins deploy.

# --------------------------------------------------------------------

def deploy():
    global CONTEXT
    if CONTEXT: raise ImportError('The plugins are already deployed')
    try:
        from ally.container import ioc, aop
    except ImportError:
        print('-' * 150, file=sys.stderr)
        print('The ally ioc or aop is missing, no idea how to deploy the application', file=sys.stderr)
        traceback.print_exc()
        print('-' * 150, file=sys.stderr)
    else:
        try:
            CONTEXT = ctx = ioc.Context()
            
            for module in aop.modulesIn('__plugin__.*', '__plugin__.*.*').load().asList():
                ctx.addSetupModule(module)
            
            ctx.addSetup(ioc.SetupEntityFixed('__setup__.ally_core.resource_manager.resourcesManager',
                app.CONTEXT.processForName('__setup__.ally_core.resource_manager.resourcesManager'), ResourcesManager))
            
            ctx.start(app.loadConfigurations('plugins'))
        except:
            print('-' * 150, file=sys.stderr)
            print('A problem occurred while deploying plugins', file=sys.stderr)
            traceback.print_exc()
            print('-' * 150, file=sys.stderr)
