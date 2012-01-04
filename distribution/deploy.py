'''
Created on Nov 24, 2011

@package: Newscoop
@copyright: 2011 Sourcefabric o.p.s.
@license: http://www.gnu.org/licenses/gpl-3.0.txt
@author: Gabriel Nistor

Provides the deployment of the distribution that contains this deploy.
'''

from inspect import stack
from pkgutil import get_importer, iter_importers
from types import ModuleType
import os
import sys
import traceback

# --------------------------------------------------------------------

_EXTEND = set()
# Used to keep the current extending package.
def deployExtendPackage():
    '''
    Provides the package extension for loaded libraries.
    '''
    loc = stack()[1][0].f_locals
    fullName, paths = loc['__name__'], loc['__path__']
    if fullName in _EXTEND: return
    
    _EXTEND.add(fullName)
    k = fullName.rfind('.')
    if k >= 0:
        package = sys.modules[fullName[:k]]
        name = fullName[k + 1:]
        importers = [get_importer(path) for path in package.__path__]
    else:
        name = fullName
        importers = iter_importers()
    
    for importer in importers:
        moduleLoader = importer.find_module(name)
        if moduleLoader and moduleLoader.is_package(name):
            path = os.path.dirname(moduleLoader.get_filename(name))
            if path not in paths:
                paths.append(path)
                module = ModuleType(fullName)
                module.__dict__['__path__'] = paths
                exec(moduleLoader.get_code(name), module.__dict__)
                # We ensure that every __init__ is called at least once.
                if getattr(module, 'deployExtendPackage', None) != deployExtendPackage:
                    raise ImportError('The package %r in path %r does not allow extension' % (name, path))
    _EXTEND.remove(fullName)

# --------------------------------------------------------------------

def setupLogging():
    import logging
    level = logging.INFO if __debug__ else logging.WARN
    logging.basicConfig(level=level,
                    format='%(asctime)s %(levelname)s (%(threadName)s %(module)s.%(funcName)s %(lineno)d): %(message)s')

def findLibraries(folder):
    '''
    Finds all the libraries (that have extension .egg) if the provided folder.
    '''
    eggs = []
    for name in os.listdir(folder):
        fullPath = os.path.join(folder, name)
        if os.path.isfile(fullPath) and fullPath.endswith('.egg'): eggs.append(fullPath)
    return eggs

def findDirs(folder):
    '''
    Finds all the directories in the provided folder.
    '''
    dirs = []
    for name in os.listdir(folder):
        fullPath = os.path.join(folder, name)
        if os.path.isdir(fullPath): dirs.append(fullPath)
    return dirs

# --------------------------------------------------------------------

if __name__ == '__main__':
    setupLogging()
    for path in findLibraries(os.path.join(os.path.dirname(__file__), 'libraries')):
        if path not in sys.path: sys.path.append(path)
    
    if True:
        for path in findDirs(os.path.join(os.path.dirname(os.path.dirname(__file__)), 'components')):
            if path not in sys.path: sys.path.append(path)
    else:
        for path in findLibraries(os.path.join(os.path.dirname(__file__), 'components')):
            if path not in sys.path: sys.path.append(path)
    #TODO: investigate why there are multiple paths of same address
    try:
        from ally import ioc, aop
    except ImportError:
        print('-' * 150, file=sys.stderr)
        print('The ally ioc or aop is missing, no idea how to deploy the application', file=sys.stderr)
        traceback.print_exc()
        print('-' * 150, file=sys.stderr)
    else:
        config = {'serverType':'cherrypy', 'ajaxCrossDomain':True, 'phpZendSupport':True}
        try:
            if False:
                import profile
                profile.run("ioc.deploy(aop.modulesIn('__setup__.*', '__setup__.*.*'), config=config)",
                            filename='output.stats')
            else: ioc.deploy(aop.modulesIn('__setup__.*', '__setup__.*.*'), config=config)
        except:
            print('-' * 150, file=sys.stderr)
            print('A problem occurred while deploying the application', file=sys.stderr)
            traceback.print_exc()
            print('-' * 150, file=sys.stderr)
