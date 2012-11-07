'''
Created on Nov 24, 2011

@package: Superdesk
@copyright: 2011 Sourcefabric o.p.s.
@license: http://www.gnu.org/licenses/gpl-3.0.txt
@author: Gabriel Nistor

Provides the deployment of the distribution that contains this deploy.
'''

from types import ModuleType
import argparse
import os
import sys
import timeit
import traceback
import warnings

# --------------------------------------------------------------------

def __deploy__():
    # Deploy the application
    try:
        import package_extender
        package_extender.PACKAGE_EXTENDER.addFreezedPackage('__deploy__.')
        from ally.container import ioc, aop
    except ImportError:
        print('Corrupted or missing ally-utilites component, make sure that this component is not missing from python path '
              'or components eggs', file=sys.stderr)
        sys.exit(1)

    application = sys.modules['application'] = ModuleType('application')
    try:
        # We create the parser to be prepared.
        application.parser = argparse.ArgumentParser(description='The ally distribution application deployer.')

        # In the first stage we prepare the application deployment.
        assembly = ioc.open(aop.modulesIn('__deploy__.*.prepare'))
        try: assembly.processStart()
        finally: ioc.deactivate()
        
        # In the second stage we parse the application arguments.
        application.options = application.parser.parse_args()
        
        # In the final stage we deploy the application.
        assembly = ioc.open(aop.modulesIn('__deploy__.*.deploy'))
        try: assembly.processStart()
        finally: ioc.deactivate()
    
    except SystemExit: raise
    except:
        print('-' * 150, file=sys.stderr)
        print('A problem occurred while deploying', file=sys.stderr)
        traceback.print_exc()
        print('-' * 150, file=sys.stderr)
        sys.exit(1)

if __name__ == '__main__':
    # First we need to set the working directory relative to the application deployer just in case the application is
    # started from somewhere else
    os.chdir(os.path.dirname(os.path.abspath(__file__)))
   
    def findLibraries(folder):
        '''Finds all the libraries (that have extension .egg or are folders) if the provided folder'''
        if os.path.isdir(folder): return (os.path.join(folder, name) for name in os.listdir(folder))
        return ()

    # Loading the libraries
    for path in findLibraries('libraries'):
        if path not in sys.path: sys.path.append(path)

    try: __import__('application_logging')
    except Exception as e: print('=' * 50, 'No logging configuration available: %s' % e)

    # Loading the components.
    for path in findLibraries('components'):
        if path not in sys.path: sys.path.append(path)

    warnings.filterwarnings('ignore', '.*already imported.*ally*')
    # To remove the warnings of pkg utils from setup tools
        
    print('=' * 50, 'Application started in %.2f seconds' % timeit.timeit(__deploy__, number=1))

