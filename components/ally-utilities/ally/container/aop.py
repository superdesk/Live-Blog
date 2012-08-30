'''
Created on Nov 28, 2011

@package: ally utilities
@copyright: 2011 Sourcefabric o.p.s.
@license: http://www.gnu.org/licenses/gpl-3.0.txt
@author: Gabriel Nistor

Provides the AOP (aspect oriented programming) support.
'''

from ..support.util_sys import searchModules, packageModules, isPackage
from ._impl.aop_container import AOPModules
from inspect import ismodule

# --------------------------------------------------------------------

class AOPError(Exception):
    '''
    Exception thrown when there is a AOP problem.
    '''

# --------------------------------------------------------------------

def modulesIn(*paths):
    '''
    Provides all the modules that are found in the provided package paths.
    
    @param paths: arguments[string|module]
        The package paths to load modules from.
    @return: AOPModules
        The found modules.
    '''
    modules = {}
    for path in paths:
        if isinstance(path, str):
            for modulePath in searchModules(path): modules[modulePath] = modulePath
        elif ismodule(path):
            if not isPackage(path):
                raise AOPError('The provided module %r is not a package' % path)
            for modulePath in packageModules(path): modules[modulePath] = modulePath
        else: raise AOPError('Cannot use path %s' % path)
    return AOPModules(modules)

def classesIn(*paths):
    '''
    Provides all the classes that are found in the provided pattern paths.
    
    @param paths: arguments[string]
        The pattern paths to load classes from.
    @return: AOPClasses
        The found classes.
    '''
    modules, filter = {}, []
    for path in paths:
        if isinstance(path, str):
            k = path.rfind('.')
            if k >= 0:
                for modulePath in searchModules(path[:k]): modules[modulePath] = modulePath
            filter.append(path)
        else: raise AOPError('Cannot use path %s' % path)
    return AOPModules(modules).classes().filter(*filter)
