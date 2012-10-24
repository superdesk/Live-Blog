'''
Created on Jan 9, 2012

@package: tests
@copyright: 2011 Sourcefabric o.p.s.
@license: http://www.gnu.org/licenses/gpl-3.0.txt
@author: Gabriel Nistor

Special module that is targeted by the application loader in order to deploy the components in the current system path.
'''

# --------------------------------------------------------------------

import ally_deploy_application as app
import os
import package_extender
import sys
import traceback
import timeit

# --------------------------------------------------------------------

def deploy(*tests):
    package_extender.PACKAGE_EXTENDER.addFreezedPackage('__setup__.')
    from ally.container import ioc, aop
    from ally.container.ioc import ConfigError, SetupError
    from ally.container.config import save, load

    if app.assembly: raise ImportError('The application is already deployed')

    try:
        isConfig = os.path.isfile(app.configurationsFilePath)
        if isConfig:
            with open(app.configurationsFilePath, 'r') as f: config = load(f)
        else: config = {}
        
        setups = aop.modulesIn('__setup__.**')
        # We need to remove the server configurations
        setups.exclude('**.server_*')

        app.assembly = ioc.open(setups, *tests, config=config)
        
        try: app.assembly.processStart()
        except (ConfigError, SetupError):
            # We save the file in case there are missing configuration
            with open(app.configurationsFilePath, 'w') as f: save(app.assembly.trimmedConfigurations(), f)
            isConfig = True
            raise
        finally:
            if not isConfig:
                with open(app.configurationsFilePath, 'w') as f: save(app.assembly.trimmedConfigurations(), f)
            ioc.deactivate()
    except:
        print('-' * 150, file=sys.stderr)
        print('A problem occurred while deploying', file=sys.stderr)
        traceback.print_exc()
        print('-' * 150, file=sys.stderr)

# --------------------------------------------------------------------

findLibraries = lambda folder: (os.path.join(folder, name) for name in os.listdir(folder))
# Finds all the libraries (that have extension .egg) if the provided folder.

def start(*tests):
    # First we need to set the working directory relative to the application deployer just in case the application is
    # started from somewhere else
    os.chdir(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
    # Loading the libraries
    for path in findLibraries('libraries'):
        if path not in sys.path: sys.path.append(path)

    # Loading the components.
    for path in findLibraries('components'):
        if path not in sys.path: sys.path.append(path)
        
    try:
        startedIn = timeit.timeit(lambda: deploy(*tests), number=1)
        print('=' * 50, 'Application started in %.2f seconds' % startedIn)
    except:
        print('=' * 50, 'Problems while deploying application')
        traceback.print_exc()
        
    return app.assembly
