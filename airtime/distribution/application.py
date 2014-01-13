'''
Created on Nov 24, 2011

@package: Superdesk
@copyright: 2011 Sourcefabric o.p.s.
@license: http://www.gnu.org/licenses/gpl-3.0.txt
@author: Gabriel Nistor

Provides the deployment of the distribution that contains this deploy.
'''

import os
import sys
import traceback
import timeit

# --------------------------------------------------------------------

findLibraries = lambda folder: (os.path.join(folder, name) for name in os.listdir(folder))
# Finds all the libraries (that have extension .egg) if the provided folder.

# --------------------------------------------------------------------

if __name__ == '__main__':
    # First we need to set the working directory relative to the application deployer just in case the application is
    # started from somewhere else
    os.chdir(os.path.dirname(os.path.abspath(__file__)))
    # Loading the libraries
    for path in findLibraries('libraries'):
        if path not in sys.path: sys.path.append(path)

    try: __import__('application_logging')
    except Exception as e: print('=' * 50, 'No logging configuration available: %s' % e)

    # Loading the components.
    for path in findLibraries('components'):
        if path not in sys.path: sys.path.append(path)

    try: import ally_deploy_application
    except ImportError:
        print('=' * 50, 'Application cannot be started, no application deploy available')
        traceback.print_exc()
    else:
        try:
            startedIn = timeit.timeit(ally_deploy_application.deploy, number=1)
            #ally_deploy_application.deploy()
            print('=' * 50, 'Application started in %.2f seconds' % startedIn)
        except:
            print('=' * 50, 'Problems while deploying application')
            traceback.print_exc()
