'''
Created on Nov 24, 2011

@package: Newscoop
@copyright: 2011 Sourcefabric o.p.s.
@license: http://www.gnu.org/licenses/gpl-3.0.txt
@author: Gabriel Nistor

Provides the deployment of the distribution that contains this deploy.
'''

from pkgutil import get_importer, iter_importers
import os
import pkgutil
import sys
import traceback

# --------------------------------------------------------------------
#TODO: document
class PackageExtender:
    
    def __init__(self):
        self._loading = set()
    
    def find_module(self, name, paths=None):
        if name not in self._loading:
            self._loading.add(name)
            loader = pkgutil.find_loader(name)
            self._loading.remove(name)
            if loader is not None: return PackageLoader(loader)
    
class PackageLoader:
    
    def __init__(self, loader):
        self.__loader = loader
    
    def load_module(self, name):
        module = self.__loader.load_module(name)
        
        if hasattr(module, '__path__'):
            fullName, paths = module.__name__, module.__path__

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
                        exec(moduleLoader.get_code(name), module.__dict__)
            module.__path__ = paths

        return module
    
    def __getattr__(self, name): return getattr(self.__loader, name)

def registerPackageExtender():
    if not sys.meta_path or not isinstance(sys.meta_path[0], PackageExtender): sys.meta_path.insert(0, PackageExtender())

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

    registerPackageExtender()

    try:
        from ally.container import ioc, aop
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
