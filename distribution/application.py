'''
Created on Nov 24, 2011

@package: Newscoop
@copyright: 2011 Sourcefabric o.p.s.
@license: http://www.gnu.org/licenses/gpl-3.0.txt
@author: Gabriel Nistor

Provides the deployment of the distribution that contains this deploy.
'''

import os
import sys
import traceback

# --------------------------------------------------------------------

def findLibraries(folder):
    '''
    Finds all the libraries (that have extension .egg) if the provided folder.
    '''
    eggs = []
    for name in os.listdir(folder):
        fullPath = os.path.join(folder, name)
        if os.path.isfile(fullPath) and fullPath.endswith('.egg'): eggs.append(fullPath)
    return eggs

# --------------------------------------------------------------------

if __name__ == '__main__':
    # First we need to set the working directory relative to the application deployer just in case the application is
    # started from somewhere else
    os.chdir(os.path.dirname(os.path.abspath(__file__)))
    # Loading the libraries
    for path in findLibraries(os.path.join(os.path.dirname(__file__), 'libraries')):
        if path not in sys.path: sys.path.append(path)
    # Loading the components.
    for path in findLibraries(os.path.join(os.path.dirname(__file__), 'components')):
        if path not in sys.path: sys.path.append(path)
    
    try: __import__('application_logging')
    except Exception as e: print('=' * 50, 'No logging configuration available: %s' % e)
    
    # register the package extender.
    try: __import__('package_extender')
    except:
        print('=' * 50, 'Application cannot be started, no package extender available')
        traceback.print_exc()
    else:
        try: import ally_deploy_application
        except ImportError: print('=' * 50, 'Application cannot be started, no application deploy available')
        else:
            try:
                file = os.path.join(os.path.dirname(__file__), ally_deploy_application.configurationsFilePath)
                ally_deploy_application.configurationsFilePath = file
                ally_deploy_application.deploy()
                print('=' * 50, 'Application deployed')
            except:
                print('=' * 50, 'Problems while deploying application')
                traceback.print_exc()
            else:
                # Loading the plugins.
                try: import ally_deploy_plugin
                except ImportError: print('=' * 50, 'No plugins deploy available, proceed without any plugin')
                else:
                    for path in findLibraries(os.path.join(os.path.dirname(__file__), 'plugins')):
                        if path not in sys.path: sys.path.append(path)
                    try:
                        file = os.path.join(os.path.dirname(__file__), ally_deploy_plugin.configurationsFilePath)
                        ally_deploy_plugin.configurationsFilePath = file
                        ally_deploy_plugin.deploy()
                        print('=' * 50, 'Plugins deployed')
                    except:
                        print('=' * 50, 'Problems while deploying plugins')
                        traceback.print_exc()
            print('=' * 50, 'Application fully started')
