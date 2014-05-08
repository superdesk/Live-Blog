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
import time
import timeit
import traceback
import warnings

# --------------------------------------------------------------------

def __deploy__():
    # Deploy the application
    try:
        import package_extender
        package_extender.PACKAGE_EXTENDER.addFreezedPackage('__deploy__.')
        from ally.container import aop, context
    except ImportError:
        print('Corrupted or missing ally component, make sure that this component is not missing from python path '
              'or components eggs', file=sys.stderr)
        sys.exit(1)

    application = sys.modules['application'] = ModuleType('application')
    try:
        # We create the parser to be prepared.
        application.parser = argparse.ArgumentParser(description='The ally distribution application deployer.')
        application.Options = object  # Prepare the option class

        # In the first stage we prepare the application deployment.
        context.open(aop.modulesIn('__deploy__.*.prepare'))
        try: context.processStart()
        finally: context.deactivate()

        # In the second stage we parse the application arguments.
        application.options = application.parser.parse_args(namespace=application.Options())

        # In the final stage we deploy the application.
        context.open(aop.modulesIn('__deploy__.*.deploy'))
        try: context.processStart()
        finally: context.deactivate()

    except SystemExit: raise
    except:
        print('-' * 150, file=sys.stderr)
        print('A problem occurred while deploying', file=sys.stderr)
        traceback.print_exc()
        print('-' * 150, file=sys.stderr)
        sys.exit(1)

def initSources():
    base = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    allyCom = os.path.join(os.path.dirname(base), 'components')
    allyPlug = os.path.join(os.path.dirname(base), 'plugins')
    lbPlug = os.path.join(base, 'plugins')
    
    flag = None
    file = None
    for arg in sys.argv:
        if flag: file = arg; break
        if arg == '-s': flag = arg
      
    sys.argv.remove(flag)
    if not file: return    
    sys.argv.remove(file)    
    
    file = os.path.join(base, file)
    if not os.path.exists(file): 
        print('Source file ', str(file), ' not found')
        return         
    
    base = None        
    sources = open(file, "r")
    for line in sources:
        if 'ALLYCOM' in line: base = allyCom
        elif 'ALLYPLUG' in line: base = allyPlug
        elif 'LBPLUG' in line: base = lbPlug
        elif base and line: sys.path.append(os.path.join(base, line.strip('\n')))  
    sources.close()


if __name__ == '__main__':
    # First we need to set the working directory relative to the application deployer just in case the application is
    # started from somewhere else
    if '-s' in sys.argv: initSources()    
    os.chdir(os.path.dirname(os.path.abspath(__file__)))
    
    def findLibraries(folder):
        '''Finds all the libraries (that have extension .egg or are folders) if the provided folder'''
        if os.path.isdir(folder): return (os.path.abspath(os.path.join(folder, name)) for name in os.listdir(folder))
        return ()

    # Loading the libraries
    for path in findLibraries('libraries'):
        if path not in sys.path: sys.path.append(path)

    # Loading the components.
    for path in findLibraries('components'):
        if path not in sys.path: sys.path.append(path)  

    warnings.filterwarnings('ignore', '.*already imported.*ally*')
    # To remove the warnings of pkg utils from setup tools

    deployTime = timeit.timeit(__deploy__, number=1)
    time.sleep(.5)  # Just a little to allow other threads to start
    print('=' * 50, 'Application started in %.2f seconds' % deployTime)

