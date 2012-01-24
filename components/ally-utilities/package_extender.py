'''
Created on Jan 9, 2012
@package: Newscoop
@copyright: 2011 Sourcefabric o.p.s.
@license: http://www.gnu.org/licenses/gpl-3.0.txt
@author: Gabriel Nistor

Provides the support for extending packages that have the same name. This module is not placed in any package to avoid
any problems in locating the extender itself.
'''

from imp import is_builtin
from pkgutil import get_importer, iter_importers, find_loader
import os
import sys
import traceback

# --------------------------------------------------------------------

class PackageExtender:
    '''
    Provides support for extending packages having the same name but different python paths. Basically provides the
    union of packages.
    '''
    
    def __init__(self):
        '''
        Construct the package extender.
        '''
        self.__loading = set()
        self.__unittest = False
        self.__unextended = set()
        
    def setForUnitTest(self, unittest):
        '''
        Sets the unit test flag indicating that the module loading should be wrapped and any problem that appears in
        importing will be reported.
        
        @param unittest: boolean
            True if the execution is intended for unit testing, False otherwise.
        '''
        assert isinstance(unittest, bool), 'Invalid unit test flag %s' % unittest
        self.__unittest = unittest
        
    def addFreezedPackage(self, name):
        '''
        Adds a new unextended package, a unextended package will only have the modules and definitions that are found
        in the package definition first found in the python path, basically this package will behave normally.
        
        @param name: string
            The name of the package to be unextended
        '''
        assert isinstance(name, str), 'Invalid package name %s' % name
        self.__unextended.add(name)
    
    def find_module(self, name, paths=None):
        '''
        @see: http://www.python.org/dev/peps/pep-0302/
        '''
        if is_builtin(name) == 0 and name not in self.__loading and name not in sys.modules:
            for unname in self.__unextended:
                if unname == name or name.startswith(unname): break
            else:
                self.__loading.add(name)
                loader = find_loader(name)
                self.__loading.remove(name)
                if loader is not None:
                    if loader.is_package(name): return PackageLoader(loader)
                    if self.__unittest: return ModuleLoader(loader)
    
class PackageLoader:
    '''
    Provides the package loader for the package extender. This is used whenever there is a package to be loaded. This
    class is just a wrapper around the normal loader that will append the package module path.
    '''
    
    def __init__(self, loader):
        '''
        Construct the package loader wrapper for the provided loader.
        
        @param loader: object
            The original loader.
        '''
        assert loader, 'A loader is required'
        self.__loader = loader
    
    def load_module(self, name):
        '''
        @see: http://www.python.org/dev/peps/pep-0302/
        '''
        module = self.__loader.load_module(name)
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

class ModuleLoader:
    '''
    Provides the module loader this is used just because when running unit tests some import exceptions get ignored and
    will really throw you off the actual problem, so this is just a wrapper that exposes any exception.
    '''
    
    def __init__(self, loader):
        '''
        Construct the module loader wrapper for the provided loader.
        
        @param loader: object
            The original loader.
        '''
        assert loader, 'A loader is required'
        self.__loader = loader
    
    def load_module(self, name):
        '''
        @see: http://www.python.org/dev/peps/pep-0302/
        '''
        try: module = self.__loader.load_module(name)
        except:
            print('-' * 150, file=sys.stderr)
            print('Problem occurred while loading module %r from loader %s' % (name, self.__loader), file=sys.stderr)
            traceback.print_exc()
            print('-' * 150, file=sys.stderr)
            raise

        return module
    
    def __getattr__(self, name): return getattr(self.__loader, name)

# --------------------------------------------------------------------

PACKAGE_EXTENDER = PackageExtender()
del PackageExtender # We remove the class so no other instance can be created.

# Registers into the python sys._meta_path the package extender.
if not sys.meta_path or not sys.meta_path[0] == PACKAGE_EXTENDER:
    sys.meta_path.insert(0, PACKAGE_EXTENDER)
        
def registerPackageExtender(unittest=True):
    '''
    Registers into the python sys._meta_path the package extender. If the package extender is registered it will not be
    registered again.
    
    @param unittest: boolean
        Flag indicating that the package extender is for unit tests.
    '''
    PACKAGE_EXTENDER.setForUnitTest(unittest)
