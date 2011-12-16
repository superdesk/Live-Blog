'''
Created on Jun 9, 2011

@package: Newscoop
@copyright: 2011 Sourcefabric o.p.s.
@license: http://www.gnu.org/licenses/gpl-3.0.txt
@author: Gabriel Nistor

Provides implementations that provide general behavior or functionality.
'''

from inspect import isclass, ismodule
import sys
import builtins
from ally.type_legacy import Callable
import inspect

# --------------------------------------------------------------------

# Flag indicating that the python version is 3k or more.
IS_PY3K = int(sys.version[:1]) >= 3

# --------------------------------------------------------------------

class Uninstantiable:
    '''
    Extending this class will not allow for the creation of any instance of the class.
    This has to be the first class inherited in order to properly work.
    '''
    
    def __new__(cls, *args, **keyargs):
        '''
        Does not allow you to create an instance.
        '''
        raise 'Cannot create an instance of "' + str(cls.__name__) + '" class'

# --------------------------------------------------------------------

class Singletone:
    '''
    Extending this class will always return the same instance.
    '''
    
    def __new__(cls):
        '''
        Will always return the same instance.
        '''
        if not hasattr(cls, '_UTIL_singletone'):
            cls._UTIL_singletone = super().__new__(cls)
        return cls._UTIL_singletone

# --------------------------------------------------------------------

_NAME_IDS = {}
# Used by the attribute to assign a unique id to a name.

_NAME_ID = lambda name: str(_NAME_IDS.setdefault(name, len(_NAME_IDS)))
# Provides the name id.

class Attribute:
    '''
    Class used for creating attributes for python objects. The purpose of this is not to directly use the the __dict__
    or getattr in order to store values in order to avoid name clashes.
    '''
    
    def __init__(self, group, name, valueType=None):
        '''
        Creates a new attribute.
        
        @param group: string
            The group name for the attribute, this is usually the module name where is created, it helps to distinguish
            between same names but with other purposes.
        @param name: string
            The name of the attribute.
        @param valueType: type
            The type to check for the set and get values.
        '''
        assert isinstance(group, str), 'Invalid group name %s' % group
        assert isinstance(name, str), 'Invalid name %s' % name
        assert not valueType or isclass(valueType), 'Invalid value type %s' % valueType
        self.__group = group
        self.__name = name
        self.__type = valueType
        if __debug__: self.__id = group + '.' + name
        else:
            self.__id = _NAME_ID(group) + '_' + _NAME_ID(name)
    
    def has(self, obj):
        '''
        Checks if there is a value for the provided object.
        
        @param obj: object
            The object to check for value.
        @return: boolean
            true if there is a value, False otherwise.
        '''
        assert obj is not None, 'An object is required'
        return hasattr(obj, self.__id)
    
    def get(self, obj, *default):
        '''
        Get the value from the provided object.
        
        @param obj: object
            The object to get the value from.
        @param default: argument
            If provided will return the default if no argument value is available.
        @return: object
            The value.
        '''
        assert obj is not None, 'An object is required'
        value = getattr(obj, self.__id, *default)
        assert not(self.__type and value is not None) or isinstance(value, self.__type), 'Invalid value %s to get for ' \
        'required type %s, for attribute %s.%s' % (value, self.__type, self.__group, self.__name)
        return value
    
    def set(self, obj, value):
        '''
        Sets the value to the provided object.
        
        @param obj: object
            The object to set the value to.
        @param value: object
            The value to set.
        @return: object
            The provided value.
        '''
        assert obj is not None, 'An object is required'
        assert not(self.__type and value is not None) or isinstance(value, self.__type), 'Invalid value %s to set for ' \
        'required type %s, for attribute %s.%s' % (value, self.__type, self.__group, self.__name)
        setattr(obj, self.__id, value)
        return value
        
    def delete(self, obj):
        '''
        Deletes the value from the provided object.
        
        @param obj: object
            The object to delete the value from.
        '''
        assert obj is not None, 'An object is required'
        delattr(obj, self.__id)
        
    def hasOwn(self, obj):
        '''
        Checks if there is a value for the provided object by using __dict__.
        
        @param obj: object
            The object to check for value.
        @return: boolean
            true if there is a value, False otherwise.
        '''
        assert obj is not None, 'An object is required'
        return self.__id in obj.__dict__
    
    def getOwn(self, obj, *default):
        '''
        Get the value from the provided object by using __dict__.
        
        @param obj: object
            The object to get the value from.
        @param default: argument
            If provided will return the default if no argument value is available.
        @return: object
            The value.
        '''
        assert obj is not None, 'An object is required'
        value = obj.__dict__.get(self.__id, *default)
        assert not(self.__type and value is not None) or isinstance(value, self.__type), 'Invalid value %s to get for ' \
        'required type %s, for attribute %s.%s' % (value, self.__type, self.__group, self.__name)
        return value
    
    def setOwn(self, obj, value):
        '''
        Sets the value to the provided object by using __dict__.
        
        @param obj: object
            The object to set the value to.
        @param value: object
            The value to set.
        @return: object
            The provided value.
        '''
        assert obj is not None, 'An object is required'
        assert not(self.__type and value is not None) or isinstance(value, self.__type), 'Invalid value %s to set for ' \
        'required type %s, for attribute %s.%s' % (value, self.__type, self.__group, self.__name)
        obj.__dict__[self.__id] = value
        return value
        
    def deleteOwn(self, obj):
        '''
        Deletes the value from the provided object by using __dict__.
        
        @param obj: object
            The object to delete the value from.
        '''
        assert obj is not None, 'An object is required'
        del obj.__dict__[self.__id]
        
    def hasDict(self, map):
        '''
        Checks if there is a value for the provided map dictionary.
        
        @param map: dictionary
            The map dictionary to check for value.
        @return: boolean
            true if there is a value, False otherwise.
        '''
        assert isinstance(map, dict), 'Invalid map %s' % map
        return self.__id in map
    
    def getDict(self, map, *default):
        '''
        Get the value from the provided map dictionary.
        
        @param map: dictionary
            The map dictionary to get the value from.
        @param default: argument
            If provided will return the default if no argument value is available.
        @return: object
            The value.
        '''
        assert isinstance(map, dict), 'Invalid map %s' % map
        value = map.get(self.__id, *default)
        assert not(self.__type and value is not None) or isinstance(value, self.__type), 'Invalid value %s to get for ' \
        'required type %s, for attribute %s.%s' % (value, self.__type, self.__group, self.__name)
        return value
    
    def setDict(self, map, value):
        '''
        Sets the value to the provided map dictionary.
        
        @param map: dictionary
            The map dictionary to set the value to.
        @param value: object
            The value to set.
        @return: object
            The provided value.
        '''
        assert isinstance(map, dict), 'Invalid map %s' % map
        assert not(self.__type and value is not None) or isinstance(value, self.__type), 'Invalid value %s to set for ' \
        'required type %s, for attribute %s.%s' % (value, self.__type, self.__group, self.__name)
        map[self.__id] = value
        return value
        
    def deleteDict(self, map):
        '''
        Deletes the value from the provided map dictionary.
        
        @param map: dictionary
            The map dictionary to delete the value from.
        '''
        assert isinstance(map, dict), 'Invalid map %s' % map
        del map[self.__id]

# --------------------------------------------------------------------

class Proxy:
    '''
    Class describing a proxy to a wrapped instance, basically this allows to override the functionality of a
    instance rather than a class.
    '''
    
    def __init__(self, wrapped):
        '''
        Constructs the proxy for the wrapped object.
        
        @param wrapped: object
            The object being wrapped by this proxy.
        '''
        assert wrapped, 'Invalid wrapped instance %s' % wrapped
        self.__dict__['_UTIL_wrapped'] = wrapped
        _overrideIsinstance()

    def __setattr__(self, name, value):
        return setattr(self.__dict__['_UTIL_wrapped'], name, value)

    def __getattr__(self, name):
        return getattr(self.__dict__['_UTIL_wrapped'], name)
    
    def __str__(self):
        return str(self.__dict__['_UTIL_wrapped'])


def _overrideIsinstance():
    '''
    FOR INTERNAL USE.
    Overrides the isinstance in order to acknowledge proxies.
    '''
    #TODO: find a different way of handling this
    # We need to change the isinstance behavior in order to convince that the proxies are just like the 
    # represented instances.
    global isinstance
    if getattr(isinstance, '_UTIL_isinstance', False): return
    __isinstance = isinstance
    def isinstance(obj, classes):
        if not __isinstance(obj, classes):
            if __isinstance(obj, Proxy):
                return __isinstance(obj.__dict__['_UTIL_wrapped'], classes)
            return False
        return True
    setattr(isinstance, '_UTIL_isinstance', True)
    setattr(builtins, 'isinstance', isinstance)
  
# --------------------------------------------------------------------

ATTR_BEAN = Attribute(__name__, 'bean', dict)
# Provides the bean properties.

def bean(clazz):
    '''
    Used for describing bean classes, this type of classes are just containers.
    '''
    properties = {}
    for name, value in clazz.__dict__.items():
        if isclass(value): properties[name] = value
    for name in properties.keys(): delattr(clazz, name)
    inherited = ATTR_BEAN.get(clazz, None)    
    if inherited: properties.update(inherited)
    
    ATTR_BEAN.set(clazz, properties)
    setattr(clazz, '__getattr__', _getattr_bean)
    setattr(clazz, '__setattr__', _setattr_bean)
    return clazz

def _getattr_bean(self, name):
    '''
    FOR INTERNAL USE.
    Used to get attributes for bean defined classes.
    '''
    if name not in ATTR_BEAN.get(self.__class__): raise AttributeError
    return None

def _setattr_bean(self, name, value):
    '''
    FOR INTERNAL USE.
    Used to get attributes for bean defined classes.
    '''
    properties = ATTR_BEAN.get(self.__class__)
    clazz = properties.get(name, None)
    if clazz:
        assert value is None or isinstance(value, clazz), \
        'Invalid value %s for name %r, expected %r' % (value, name, clazz.__name__)
    object.__setattr__(self, name, value)

# --------------------------------------------------------------------

def findInValues(dictionary, value):
    '''
    Searches in the provided dictionary the value as an entry in the dictionary values.
    
    @param dictionary: dictionary
        The dictionary to search the values.
    @param value: object
        The value to search in the dictionary values.
    @return: key|None
        Either the found key, or None.
    '''
    assert isinstance(dictionary, dict), 'Invalid dictionary %s' % dictionary
    for key, values in dictionary.items():
        if value in values:
            return key

def findOnEscapedKey(key, regexEscape, items, prefix=None):
    '''
    Finds in the items dictionary the item that has the key matching the provided key by using the escaping regex.
    
    @param key: string
        The key to search.
    @param regexEscape: regex
        The regex used for escaping also the provided key and the dictionary keys.
    @param items: Iterable
        Aitems iterable, basically a iterable with a tuple of key-value pair.
    @param prefix: string|None
        If provided will match the provided key only if the search key starts with the prefix and the matching 
        will be done by removing the prefix from the search keys. 
    '''
    for skey, item in items:
        if not prefix or skey.startswith(prefix):
            escaped = ''.join(regexEscape.findall(key))
            if escaped == ''.join(regexEscape.findall(skey[len(prefix):] if prefix else skey)):
                return item

# --------------------------------------------------------------------

def replaceInFile(fileObj, replacements):
    '''
    Creates a proxy for the provided file object that will replace in the provided file content based on the data
    provided in the replacements map.
    
    @param fileObj: a file like object with a 'read' method
        The file object to wrap and have the content changed.
    @param replacements: dictionary{string|bytes, string|bytes}
        A dictionary containing as a key the data that needs to be changed and as a value the data to change with.
    @return: Proxy
        The proxy created for the file that will handle the data replacing.
    '''
    assert hasattr(fileObj, 'read'), 'Invalid file object %s does not have a read method' % fileObj
    assert isinstance(replacements, dict), 'Invalid replacements dictionary %s' % replacements
    
    proxy = Proxy(fileObj)
    proxy.__dict__['read'] = _ProxyRead(fileObj, replacements)
    return proxy

class _ProxyRead(Callable):
    '''
    FOR INTERNAL USE.
    Used by the @see: replaceInFile method.
    '''
    
    def __init__(self, fileObj, replacements):
        self.__fileObj = fileObj
        self.__replacements = replacements
        
        self.__maxKey = 0
        for key in replacements.keys():
            if self.__maxKey < len(key): self.__maxKey = len(key)
            
        self.__leftOver = None
    
    def __call__(self, count=None):
        data = self.__fileObj.read(count)
        
        if not data:
            if self.__leftOver:
                data = self.__leftOver
                self.__leftOver = None
            else: return data
        
        toIndex = None
        if self.__leftOver:
            toIndex = len(data)
            data = self.__leftOver + data
        else:
            extra = self.__fileObj.read(self.__maxKey - 1)
            if extra:
                toIndex = len(data)
                data = data + extra
                
        for key, value in self.__replacements.items(): data = data.replace(key, value)
        
        if toIndex:
            self.__leftOver = data[toIndex:]
            data = data[:toIndex]
        
        return data

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
    stack = inspect.stack()
    currentModule = stack[level][1]
    for k in range(level + 1, len(stack)):
        if stack[k][1] != currentModule:
            frame = stack[k][0]
            break
    else: raise 'There is no other module than the current one'
    return frame.f_locals
