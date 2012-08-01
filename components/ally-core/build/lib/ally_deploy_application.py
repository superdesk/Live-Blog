'''
Created on Jan 9, 2012

@package: Newscoop
@copyright: 2011 Sourcefabric o.p.s.
@license: http://www.gnu.org/licenses/gpl-3.0.txt
@author: Gabriel Nistor

Special module that is targeted by the application loader in order to deploy the components in the current system path.
'''

# --------------------------------------------------------------------

import os
import package_extender
import sys
import traceback

# --------------------------------------------------------------------

configurationsFilePath = 'application.properties'
# The name of the configuration file

assembly = None
# The assembly for the application resources

# --------------------------------------------------------------------

def deploy():
    package_extender.PACKAGE_EXTENDER.addFreezedPackage('__setup__.')
    from ally.container import ioc, aop
    from ally.container.ioc import ConfigError, SetupError
    from ally.container.config import save, load

    global assembly
    if assembly: raise ImportError('The application is already deployed')

    try:
        isConfig = os.path.isfile(configurationsFilePath)
        if isConfig:
            with open(configurationsFilePath, 'r') as f: config = load(f)
        else: config = {}

        assembly = ioc.open(aop.modulesIn('__setup__.**'), config=config)
        try: assembly.processStart()
        except (ConfigError, SetupError):
            # We save the file in case there are missing configuration
            with open(configurationsFilePath, 'w') as f: save(assembly.trimmedConfigurations(), f)
            isConfig = True
            raise
        finally:
            if not isConfig:
                with open(configurationsFilePath, 'w') as f: save(assembly.trimmedConfigurations(), f)
            ioc.deactivate()
    except:
        print('-' * 150, file=sys.stderr)
        print('A problem occurred while deploying', file=sys.stderr)
        traceback.print_exc()
        print('-' * 150, file=sys.stderr)
