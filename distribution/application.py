'''
Created on Nov 24, 2011

@package: Newscoop
@copyright: 2011 Sourcefabric o.p.s.
@license: http://www.gnu.org/licenses/gpl-3.0.txt
@author: Gabriel Nistor

Provides the deployment of the distribution that contains this deploy.
'''

import os
import profile
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
    applicationProfile, pluginsProfile = False, False

    # Loading the libraries
    for path in findLibraries(os.path.join(os.path.dirname(__file__), 'libraries')):
        if path not in sys.path: sys.path.append(path)
    # Loading the components.
    for path in findLibraries(os.path.join(os.path.dirname(__file__), 'components')):
        if path not in sys.path: sys.path.append(path)
    
    try: import application_logging
    except: traceback.print_exc()
    
    # register the package extender.
    try: import package_extender
    except: traceback.print_exc()
    
    try:
        import ally_deploy_application
        file = os.path.join(os.path.dirname(__file__), ally_deploy_application.configurationsFilePath)
        ally_deploy_application.configurationsFilePath = file
        if applicationProfile: profile.run('ally_application_deploy.deploy()', filename='output.stats')
        else: ally_deploy_application.deploy()
        print('=' * 50, 'Application deployed')
    except: traceback.print_exc()
    else:
        # Loading the plugins. 
        for path in findLibraries(os.path.join(os.path.dirname(__file__), 'plugins')):
            if path not in sys.path: sys.path.append(path)
        
        try:
            import ally_deploy_plugin
            file = os.path.join(os.path.dirname(__file__), ally_deploy_plugin.configurationsFilePath)
            ally_deploy_plugin.configurationsFilePath = file
            if pluginsProfile: profile.run('ally_deploy_plugin.deploy()', filename='output.stats')
            else: ally_deploy_plugin.deploy()
            print('=' * 50, 'Plugins deployed')
        except: traceback.print_exc()
    print('=' * 50, 'Application fully started')
