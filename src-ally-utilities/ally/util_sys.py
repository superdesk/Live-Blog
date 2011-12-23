'''
Created on Dec 19, 2011

@package: Newscoop
@copyright: 2011 Sourcefabric o.p.s.
@license: http://www.gnu.org/licenses/gpl-3.0.txt
@author: Gabriel Nistor

Provides utility methods for handling system packages/modules/classes.
'''

from inspect import isclass, ismodule, stack
import sys
import pkgutil
import re
import os

# --------------------------------------------------------------------

def fullyQName(obj):
    '''
    Provides the fully qualified class name of the instance or class provided.
    
    @param obj: class|object
        The class or instance to provide the fully qualified name for.
    '''
    if not isclass(obj):
        obj = obj.__class__
    return obj.__module__ + '.' + obj.__name__

def classForName(name):
    '''
    Provides the class for the provided fully qualified name of a class.
    
    @param name: string
        The fully qualified class name,
    @return: class
        The class of the fully qualified name.
    '''
    parts = name.split(".")
    module_name = ".".join(parts[:-1])
    class_name = parts[-1]
    if module_name == "":
        if class_name not in sys.modules: return __import__(class_name)
        return sys.modules[class_name]
    else:
        if module_name not in sys.modules:__import__(module_name)
        return getattr(sys.modules[module_name], class_name)

def exceptionModule(e):
    '''
    Finds the module in which the provided exception occurred.
    
    @param e: Exception
        The exception to find the module for.
    @return: module|None
        THe found module or None.
    '''
    assert isinstance(e, Exception), 'Invalid exception %s' % e
    tb = e.__traceback__
    while tb.tb_next is not None:
        tb = tb.tb_next
    fileName = tb.tb_frame.f_code.co_filename
    for m in sys.modules.values():
        if getattr(m, '__file__', None) == fileName:
            return m
    return None

def exceptionModuleName(e):
    '''
    Finds the module name in which the provided exception occurred.
    
    @param e: Exception
        The exception to find the module for.
    @return: string|None
        THe found module name or None.
    '''
    m = exceptionModule(e)
    if m is not None:
        return m.__name__
    return None

def isPackage(module):
    '''
    Checks if the provided module is a package.
    
    @param module: module
        The module to be checked.
    '''
    assert ismodule(module), 'Invalid module %s' % module
    return hasattr(module, '__path__')

def callerLocals(level=1):
    '''
    Provides the calling module locals.
    
    @param level: integer
        The level from where to start finding the caller.
    @return: dictionary{string, object}
        The locals of the caller (based on the provided level)
    '''
    stacks = stack()
    currentModule = stacks[level][1]
    for k in range(level + 1, len(stacks)):
        if stacks[k][1] != currentModule:
            frame = stacks[k][0]
            break
    else: raise Exception('There is no other module than the current one')
    return frame.f_locals

def searchModules(pattern):
    '''
    Finds all modules available in the sys.path that respect the provided pattern. The search is done directly on the
    importers based on PEP 302. Basically this search guarantees that all modules that are defined (even if some might
    not be imported) respecting the pattern will be obtained.
    
    @param pattern: string
        The pattern is formed based on full module name, ex:
        
            __setup__
            Will return a map with the key setup and the values will contain all the paths that define a __setup__
            module.
            
            __setup__.*
            Will return all the modules that are found in __setup__ package.
            
            __setup__.*_http
            Will return all the modules that are found in __setup__ package that end with _http.
    @return: dictionary{string, list[string]}
        A dictionary containing as a key the module full name, and as a value a list of paths where this module is
        defined.
    '''
    assert isinstance(pattern, str), 'Invalid module pattern %s' % pattern
    modules, importers = {}, None
    k = pattern.rfind('.')
    if k >= 0:
        name = pattern[k + 1:]
        parent = searchModules(pattern[:k])
        if name.find('*') >= 0:
            matcher = re.compile('[a-zA-Z0-9_]*'.join([re.escape(e) for e in name.split('*')]))
            for pckg, pckgPaths in parent.items():
                packages = []
                for path in pckgPaths:
                    moduleLoader = pkgutil.get_importer(os.path.dirname(path)).find_module(pckg)
                    if moduleLoader and moduleLoader.is_package(pckg): packages.append(path)
                for moduleLoader, modulePath, _isPckg in pkgutil.iter_modules(packages):
                    if matcher.match(modulePath):
                        path = os.path.dirname(moduleLoader.find_module(modulePath).get_filename(modulePath))
                        paths = modules.setdefault(pckg + ('.' if pckg else '') + modulePath, [])
                        if path not in paths: paths.append(path)
            return modules
        else: importers = [(pckg, pkgutil.get_importer(path)) for pckg, paths in parent.items() for path in paths ]
    else:
        name = pattern
        importers = [('', imp) for imp in pkgutil.iter_importers()]
    
    for package, importer in importers:
        moduleLoader = importer.find_module(name)
        if moduleLoader:
            path = os.path.dirname(moduleLoader.get_filename(name))
            paths = modules.setdefault(package + ('.' if package else '') + name, [])
            if path not in paths: paths.append(path)
    return modules

def packageModules(package):
    '''
    Provides all modules that are found in the provided module package.
    
    @param package: module
        The module package to get the modules from.
    @return: dictionary{string, list[string]}
        A dictionary containing as a key the module full name, and as a value a list of paths where this module is
        defined.
    '''
    assert ismodule(package), 'Invalid module %s' % package
    assert isPackage(package), 'Invalid package module %s' % package
    modules = {}
    for moduleLoader, modulePath, _isPckg in pkgutil.iter_modules(package.__path__, package.__name__ + '.'):
        path = os.path.dirname(moduleLoader.find_module(modulePath).get_filename(modulePath))
        paths = modules.setdefault(modulePath, [])
        if path not in paths: paths.append(path)
    return modules
