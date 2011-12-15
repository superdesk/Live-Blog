'''
Created on Jun 9, 2011

@package: Newscoop
@copyright: 2011 Sourcefabric o.p.s.
@license: http://www.gnu.org/licenses/gpl-3.0.txt
@author: Gabriel Nistor

Provides implementations that provide general behavior or functionality.
'''

from inspect import isclass
import sys
import builtins
from ally.type_legacy import Callable

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
        raise AssertionError('Cannot create an instance of "' + str(cls.__name__) + '" class')

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

def bean(clazz):
    '''
    Used for describing bean classes, this type of classes are just containers.
    '''
    properties = {}
    for name, value in clazz.__dict__.items():
        if isclass(value): properties[name] = value
    for name in properties.keys(): delattr(clazz, name)
    inherited = getattr(clazz, '_UTIL_bean', None)    
    if inherited: properties.update(inherited)
    
    setattr(clazz, '_UTIL_bean', properties)
    setattr(clazz, '__getattr__', _getattr_bean)
    setattr(clazz, '__setattr__', _setattr_bean)
    return clazz

def _getattr_bean(self, name):
    '''
    FOR INTERNAL USE.
    Used to get attributes for bean defined classes.
    '''
    if name not in getattr(self.__class__, '_UTIL_bean'): raise AttributeError
    return None

def _setattr_bean(self, name, value):
    '''
    FOR INTERNAL USE.
    Used to get attributes for bean defined classes.
    '''
    properties = getattr(self.__class__, '_UTIL_bean')
    clazz = properties.get(name, None)
    if clazz:
        assert value is None or isinstance(value, clazz), \
        'Invalid value %s for name %r, expected %r' % (value, name, simpleName(clazz))
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
    Creates a proxy for the provided file object that will replace in the provided file object content the data
    provided in the replacements map.
    
    @param fileObj: a file like object with a 'read' method
        The file object to wrap and have the content changed.
    @param replacements: dictionary
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
        self.fileObj = fileObj
        self.replacements = replacements
        
        self.maxKey = 0
        for key in replacements.keys():
            if self.maxKey < len(key): self.maxKey = len(key)
            
        self.leftOver = None
    
    def __call__(self, count=None):
        data = self.fileObj.read(count)
        
        if not data:
            if self.leftOver:
                data = self.leftOver
                self.leftOver = None
            else: return data
        
        toIndex = None
        if self.leftOver:
            toIndex = len(data)
            data = self.leftOver + data
        else:
            extra = self.fileObj.read(self.maxKey - 1)
            if extra:
                toIndex = len(data)
                data = data + extra
                
        for key, value in self.replacements.items(): data = data.replace(key, value)
        
        if toIndex:
            self.leftOver = data[toIndex:]
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

def simpleName(obj):
    '''
    Provides the simple class name of the instance or class provided.
    
    @param obj: class|object
        The class or instance to provide the simple class name for.
    '''
    if not isclass(obj):
        obj = obj.__class__
    return obj.__name__

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
