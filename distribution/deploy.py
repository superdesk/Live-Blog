'''
Created on Nov 24, 2011

@package: Newscoop
@copyright: 2011 Sourcefabric o.p.s.
@license: http://www.gnu.org/licenses/gpl-3.0.txt
@author: Gabriel Nistor

Provides the deployment of the distribution that contains this deploy.
'''

import sys
import traceback
import os
import extender

# --------------------------------------------------------------------

deployExtendPackage = extender.deployExtendPackage

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


if __name__ == '__main__':
    for path in findLibraries(os.path.join(os.path.dirname(__file__), 'libraries')):
        if path not in sys.path: sys.path.append(path)
        
    for path in findLibraries(os.path.join(os.path.dirname(__file__), 'components')):
        if not path.count('ally-ioc'):
            if path not in sys.path: sys.path.append(path)
    
    sys.path.append('e:/Sourcefabric/Workspace/src-ally-ioc')
    #TODO: investigate why there are multiple paths of same address
    try:
        from ally import ioc
    except ImportError:
        print('-' * 150, file=sys.stderr)
        print('The ally.ioc is missing, no idea how to deploy the application', file=sys.stderr)
        traceback.print_exc()
        print('-' * 150, file=sys.stderr)
    else:
        config = {'serverType':'cherrypy', 'ajaxCrossDomain':True, 'phpZendSupport':True}
        try:
            if False:
                import profile
                profile.run("ioc.assemble(ioc.modulesIn('__setup__.*', '__setup__.*.*'), config=config)",
                            filename='output.stats')
            else: ioc.assemble(ioc.modulesIn('__setup__.*', '__setup__.*.*'), config=config)
        except:
            print('-' * 150, file=sys.stderr)
            print('A problem occurred while deploying the application', file=sys.stderr)
            traceback.print_exc()
            print('-' * 150, file=sys.stderr)
