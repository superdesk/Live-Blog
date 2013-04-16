'''
Created on Dec 19, 2011

@package: ally base
@copyright: 2011 Sourcefabric o.p.s.
@license: http://www.gnu.org/licenses/gpl-3.0.txt
@author: Gabriel Nistor

Provides utility functions for handling system packages/modules/classes.
'''

from collections import deque
from inspect import isclass, ismodule, stack, isfunction, getsourcelines, \
    getsourcefile, ismethod
from os.path import dirname, relpath
from pkgutil import iter_modules, get_importer, iter_importers, \
    iter_importer_modules
import re
import sys

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

def locationStack(located):
    '''
    Provides a stack message for the provided located element, the stack will look as being part of a exception. This is 
    used whenever you want to indicate where the problem occurred even if the data is post processed and the actual stack
    will not reflect the actual method.
    
    @param located: function|class
        The function or class to construct the stack message based on.
    @return: string
        The stack message.
    '''
    if isclass(located):
        try: _src, line = getsourcelines(located)
        except IOError: return '\n  Generated class "%s.%s"' % (located.__module__, located.__name__)
        return '\n  File "%s", line %i' % (getsourcefile(located), line)
    else:
        assert isfunction(located) or ismethod(located), 'Invalid function or class %s' % located
        return '\n  File "%s", line %i, in %s' % (located.__code__.co_filename, located.__code__.co_firstlineno,
                                                  located.__name__)

def isPackage(module):
    '''
    Checks if the provided module is a package.
    
    @param module: module
        The module to be checked.
    '''
    assert ismodule(module), 'Invalid module %s' % module
    return hasattr(module, '__path__')

def callerGlobals(level=1):
    '''
    Provides the caller globals.
    
    @param level: integer
        The level from where to start finding the caller.
    @return: dictionary{string, object}
        The globals of the caller (based on the provided level)
    '''
    stacks = stack()
    currentModule = stacks[level][1]
    for k in range(level + 1, len(stacks)):
        if stacks[k][1] != currentModule:
            frame = stacks[k][0]
            break
    else: raise Exception('There is no other module than the current one')
    return frame.f_globals

def callerLocals(level=1):
    '''
    Provides the caller locals.
    
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

def pythonPath(level=1):
    '''
    Provides the python path where the calling module is defined
    
    @param level: integer
        The level from where to start finding the module.
    @return: string
        The relative python path of the calling module.
    '''
    gl = callerGlobals(level)
    moduleName, modulePath = gl['__name__'], gl['__file__']
    if modulePath.endswith('__init__.py'): modulePath = dirname(modulePath)
    for _k in range(0, moduleName.count('.') + 1):
        modulePath = dirname(modulePath)
    return relpath(modulePath)

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
            
            __setup__.**
            Will return all the modules and sub modules that are found in __setup__ package.
            
            __setup__.*_http
            Will return all the modules that are found in __setup__ package that end with _http.
    @return: dictionary{tuple(boolean, string), list[string]}
        A dictionary containing as a key a tuple with a flag indicating that the the module full name, and as a value a list of paths where this module is
        defined.
    '''
    return {keyPack[1]: paths for keyPack, paths in searchPaths(pattern).items()}

def searchPaths(pattern):
    '''
    Finds all modules/packages available in the sys.path that respect the provided pattern. The search is done directly on the
    importers based on PEP 302. Basically this search guarantees that all modules that are defined (even if some might
    not be imported) respecting the pattern will be obtained.
    
    @param pattern: string
        The pattern is formed based on full module name, ex:
        
            __setup__
            Will return a map with the key setup and the values will contain all the paths that define a __setup__
            module.
            
            __setup__.*
            Will return all the modules that are found in __setup__ package.
            
            __setup__.**
            Will return all the modules and sub modules that are found in __setup__ package.
            
            __setup__.*_http
            Will return all the modules that are found in __setup__ package that end with _http.
    @return: dictionary{tuple(boolean, string), list[string]}
        A dictionary containing as a key a tuple with a flag indicating that the full name is a package and as a second value the package/module full path,
        and as a value a list of paths where this package/module is defined.
    '''
    assert isinstance(pattern, str), 'Invalid module pattern %s' % pattern
    modules, importers = {}, None
    k = pattern.rfind('.')
    if k >= 0:
        name = pattern[k + 1:]
        parent = searchPaths(pattern[:k])

        if name == '**':
            while parent:
                keyPack, pckgPaths = parent.popitem()
                isPackage, pckg = keyPack
                for path in pckgPaths:
                    if isPackage:
                        moduleImporter = get_importer(path)
                        for modulePath, isPkg in iter_importer_modules(moduleImporter):
                            path = dirname(moduleImporter.find_module(modulePath).get_filename(modulePath))
                            keyPack = (isPkg, pckg + ('.' if pckg else '') + modulePath)
                            if isPkg:
                                paths = parent.get(keyPack)
                                if paths is None: paths = parent[keyPack] = []
                                if path not in paths: paths.append(path)

                            paths = modules.get(keyPack)
                            if paths is None: paths = modules[keyPack] = []
                            if path not in paths: paths.append(path)
            return modules
        elif name.find('*') >= 0:
            matcher = re.compile('[a-zA-Z0-9_]*'.join([re.escape(e) for e in name.split('*')]))
            for keyPack, pckgPaths in parent.items():
                isPackage, pckg = keyPack
                for path in pckgPaths:
                    if isPackage:
                        moduleImporter = get_importer(path)
                        for modulePath, isPkg in iter_importer_modules(moduleImporter):
                            if matcher.match(modulePath):
                                path = dirname(moduleImporter.find_module(modulePath).get_filename(modulePath))
                                keyPack = (isPkg, pckg + ('.' if pckg else '') + modulePath)
                                paths = modules.get(keyPack)
                                if paths is None: paths = modules[keyPack] = []
                                if path not in paths: paths.append(path)
            return modules
        else: importers = [(keyPack[0], keyPack[1], get_importer(path)) for keyPack, paths in parent.items() for path in paths]
    else:
        name = pattern
        importers = [(True, '', imp) for imp in iter_importers()]

    for isPackage, package, importer in importers:
        if isPackage:
            moduleLoader = importer.find_module(name)
            if moduleLoader:
                path = dirname(moduleLoader.get_filename(name))
                keyPack = (moduleLoader.is_package(name), package + ('.' if package else '') + name)
            else: keyPack = None
        elif package == name or package.endswith('.' + name):
            nameMod = name
            kk = nameMod.rfind('.')
            if kk >= 0: nameMod = nameMod[kk + 1:]
            moduleLoader = importer.find_module(nameMod)
            path = dirname(moduleLoader.get_filename(nameMod))
            keyPack = (False, package)
        else: keyPack = None

        if keyPack:
            paths = modules.get(keyPack)
            if paths is None: paths = modules[keyPack] = []
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
    for moduleLoader, modulePath, _isPckg in iter_modules(package.__path__, package.__name__ + '.'):
        path = dirname(moduleLoader.find_module(modulePath).get_filename(modulePath))
        paths = modules.setdefault(modulePath, [])
        if path not in paths: paths.append(path)
    return modules

def getAttrAndClass(clazz, name):
    '''
    The getattr function provides only the required attribute value, this function provides the attribute value and 
    also the class or super class that defines the attribute.
    Attention unlike getattr this search will not invoke descriptors.
    
    @param clazz: class
        The class to get the attribute from.
    @param name: string
        The attribute name.
    @return: tuple(object, class)
        A tuple containing in the first position the attribute value and in the second position the class that
        defined the attribute.
    '''
    assert isclass(clazz), 'Invalid class %s' % clazz
    assert isinstance(name, str), 'Invalid name %s' % name
    classes = deque()
    classes.append(clazz)
    while classes:
        cls = classes.popleft()
        if cls == object: continue
        if name in cls.__dict__: return cls.__dict__[name], cls
        classes.extend(cls.__bases__)
    raise AttributeError('The %s has not attribute %r' % (clazz, name))

def validateTypeFor(clazz, name, vauleType, allowNone=True):
    '''
    Creates a property descriptor inside a class that provides a getter and a setter that validates the
    set value against the provided value type.
    
    @param clazz: class
        The class to validate the property for.
    @param name: string
        The name to use for the property.
    @param vauleType: class|tuple(class)
        The required type of the value to be set.
    @param allowNone: boolean
        If True will allow also the None value to be set, otherwise only values of type clazz are allowed.
    '''
    assert isclass(clazz), 'Invalid class %s' % clazz
    assert isinstance(name, str), 'Invalid name %s' % name
    assert isclass(vauleType) or isinstance(vauleType, tuple), 'Invalid value type %s' % clazz
    assert isinstance(allowNone, bool), 'Invalid allow flag %s' % allowNone

    try:
        descriptor, _clazz = getAttrAndClass(clazz, name)

        get = getattr(descriptor, '__get__')

        descriptor.__set__  # Just to raise AttributeError in case there is no __set__ on the descriptor
        def set(self, value):
            if not ((allowNone and value is None) or isinstance(value, vauleType)):
                raise ValueError('Invalid value %s for class %s' % (value, vauleType))
            descriptor.__set__(self, value)

        delete = getattr(descriptor, '__delete__', None)
    except AttributeError:
        get = lambda self: getattr(self, name)

        def set(self, value):
            if not ((allowNone and value is None) or isinstance(value, vauleType)):
                raise ValueError('Invalid value %s for class %s' % (value, vauleType))
            self.__dict__[name] = value

        def delete(self):
            del self.__dict__[name]

    setattr(clazz, name, property(get, set, delete))

def validateType(name, vauleType, allowNone=True):
    '''
    Decorator for @see: validateTypeFor that will only apply the validation if the application is in debug mode.
    
    @param name: string
        The name to use for the property.
    @param vauleType: class|tuple(class)
        The required type of the value to be set.
    @param allowNone: boolean
        If True will allow also the None value to be set, otherwise only values of type clazz are allowed.
    '''
    def decorator(clazz):
        if __debug__: validateTypeFor(clazz, name, vauleType, allowNone)
        return clazz
    return decorator
