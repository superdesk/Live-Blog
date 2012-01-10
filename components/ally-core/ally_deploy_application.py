'''
Created on Jan 9, 2012

@package: Newscoop
@copyright: 2011 Sourcefabric o.p.s.
@license: http://www.gnu.org/licenses/gpl-3.0.txt
@author: Gabriel Nistor

Special module that is targeted by the application loader in order to deploy the components in the current system path.
'''

from configparser import ConfigParser
import json
import package_extender
import sys
import traceback

# --------------------------------------------------------------------

package_extender.registerPackageExtender(False)
# register the package extender.

CONFIGURATIONS = ConfigParser()
# The configurations for the application

CONTEXT = None
# The context of the deploy.

# --------------------------------------------------------------------
#TODO: de facut configurile ca json simplu
def loadConfigurations(section):
    if CONFIGURATIONS.has_section(section):
        return {name:json.loads(value) for name, value in CONFIGURATIONS.items(section)}

def deploy():
    global CONTEXT
    if CONTEXT: raise ImportError('The application is already deployed')
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
            
            for module in aop.modulesIn('__setup__.**').load().asList():
                ctx.addSetupModule(module)
            
            ctx.start(loadConfigurations('application'))
        except:
            print('-' * 150, file=sys.stderr)
            print('A problem occurred while deploying', file=sys.stderr)
            traceback.print_exc()
            print('-' * 150, file=sys.stderr)
