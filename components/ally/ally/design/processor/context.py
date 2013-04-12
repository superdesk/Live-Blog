'''
Created on Jun 12, 2012

@package: ally base
@copyright: 2012 Sourcefabric o.p.s.
@license: http://www.gnu.org/licenses/gpl-3.0.txt
@author: Gabriel Nistor

Provides the context support.
'''

from .spec import IAttribute, IResolver, Resolvers, ContextMetaClass
from ally.support.util import immut

# --------------------------------------------------------------------

ALLOWED = {'__module__', '__doc__', '__locals__'}
# The allowed keys in the namespace.

# --------------------------------------------------------------------

def definerContext(name, bases, namespace):
    '''
    Process the provided context definition parameters.
        
    @param name: string
        The class name.
    @param bases: tuple(class)
        The inherited classes.
    @param namespace: dictionary{string, object}
        The context name space definition.
    @return: tuple(string, tuple(classes), dictionary{string, object})
        The name, basses and namespace to use in constructing the context class.
    '''
    assert isinstance(namespace, dict), 'Invalid namespace %s' % namespace
    assert isinstance(bases, tuple), 'Invalid bases %s' % bases
    assert bases, 'At least one base class is required'
    
    attributes = {}
    for key, value in namespace.items():
        if key in ALLOWED: continue
        if not isinstance(value, IAttribute):
            raise TypeError('Invalid attribute \'%s\' for name \'%s\'' % (value, key))
        attributes[key] = value
    for key in attributes: namespace.pop(key)
    
    # Adding also the parent attributes.
    for base in bases:
        if base is Context: continue
        if not isinstance(base, ContextMetaClass):
            raise TypeError('A context class can only inherit other context classes, invalid class %s' % base)
        assert isinstance(base, ContextMetaClass)
        if base.__definer__ != definerContext:
            raise TypeError('Cannot define because of inherited context class %s' % base)
        
        for key, attribute in base.__attributes__.items():
            if key not in attributes: attributes[key] = attribute
    
    namespace['__attributes__'] = immut(attributes)
    return name, bases, namespace
        
def definerObject(name, bases, namespace):
    '''
    Process the provided object definition parameters.
        
    @param name: string
        The class name.
    @param bases: tuple(class)
        The inherited classes.
    @param namespace: dictionary{string, object}
        The context name space definition.
    @return: tuple(string, tuple(classes), dictionary{string, object})
        The name, basses and namespace to use in constructing the context class.
    '''
    assert isinstance(namespace, dict), 'Invalid namespace %s' % namespace
    assert isinstance(bases, tuple), 'Invalid bases %s' % bases
    assert bases == (Object,), 'No bases are allowed for object contexts other then Object'
    assert '__attributes__' in namespace, 'No attributes defined for context object'
    
    namespace['__slots__'] = tuple(namespace['__attributes__'])
    return name, bases, namespace

# --------------------------------------------------------------------

class Context(metaclass=ContextMetaClass):
    '''
    The base context class, this class needs to be inherited by all classes that need to behave like a data context definition
    only, no objects for this contexts can be created.
    '''
    __definer__ = definerContext

    @classmethod
    def __subclasshook__(cls, C):
        '''
        Assigned to the context as the __subclasshook__ method.
        '''
        if not isinstance(cls, ContextMetaClass): return NotImplemented
        if not isinstance(C, ContextMetaClass): return False
        assert isinstance(cls, ContextMetaClass)
        
        for attribute in cls.__attributes__.values():
            assert isinstance(attribute, IAttribute)
            if not attribute.isValid(C): return False
        return True
    
    def __new__(cls, *args, **keyargs):
        '''
        Assigned to the context as the __new__ method in order to prevent creation.
        '''
        raise TypeError('Cannot create an instance for %s' % cls)
    
class Object(metaclass=ContextMetaClass):
    '''
    The base object context class, this class needs to be inherited by all classes that need to behave like a data context that
    can have object created.
    '''
    __definer__ = definerObject
    
    __subclasshook__ = Context.__subclasshook__
    
    def __init__(self, **keyargs):
        '''
        Assigned to the context as the __init__ method.
        '''
        for name, value in keyargs.items(): setattr(self, name, value)
    
    def __getattr__(self, name):
        '''
        Assigned to the context whenever the application is in not in debug mode and there is no need to perform validations.
        '''
        if name in self.__attributes__: return None
        raise AttributeError('Unknown attribute \'%s\'' % name)
    
    def __contains__(self, attribute):
        '''
        Assigned to the context as the __contains__ method.
        
        @param attribute: tuple(string, IAttribute) or descriptor with '__name__' and '__objclass__'
            The attribute to check if contained.
        '''
        if attribute is None: return False
        if not isinstance(attribute, IAttribute):
            try: name, clazz = attribute.__name__, attribute.__objclass__
            except AttributeError: return False
                
            if not isinstance(clazz, ContextMetaClass): return False
            assert isinstance(clazz, ContextMetaClass)
            attribute = clazz.__attributes__.get(name)
            
            if not isinstance(attribute, IAttribute): return False
            assert isinstance(attribute, IAttribute)
        
        return attribute.isIn(self.__class__)
    
    def __str__(self):
        '''
        Assigned to the context as the __str__ method.
        '''
        namesValues = ((name, getattr(self, name)) for name, attr in self.__attributes__.items() if attr in self)
        attrs = ', '.join('%s=%s' % nameValue for nameValue in namesValues)
        return '%s(%s)' % (self.__class__.__name__, attrs)

# --------------------------------------------------------------------

def create(resolvers):
    '''
    Creates the object contexts for the provided resolvers.
    
    @param resolvers: Resolvers
        The resolvers to create the context for.
    '''
    contexts = {}
    for nameContext, forContext in groupResolversByContext(resolvers).items():
        attributes = {}
        for resolver in forContext.values(): resolver.create(attributes)
        namespace = dict(__module__=__name__, __attributes__=attributes)
        contexts[nameContext] = type('Object$%s%s' % (nameContext[0].upper(), nameContext[1:]), (Object,), namespace)

    return contexts

def createDefinition(resolvers):
    '''
    Creates the definition contexts for the provided resolvers.
    
    @param resolvers: Resolvers
        The resolvers to create the context for.
    '''
    contexts = {}
    for nameContext, forContext in groupResolversByContext(resolvers).items():
        namespace = dict(__module__=__name__)
        for resolver in forContext.values(): resolver.createDefinition(namespace)
        contexts[nameContext] = type('Context%s%s' % (nameContext[0].upper(), nameContext[1:]), (Context,), namespace)

    return contexts

def groupResolversByContext(resolvers):
    '''
    Groups the resolvers from the provided resolvers repository based on context.
    
    @param resolvers: Resolvers
        The resolvers to group by.
    @return: dictionary{string: dictionary{string: IResolver}}
        The grouped resolvers, first dictionary key is the context name and second dictionary key is the attribute name.
    '''
    assert isinstance(resolvers, Resolvers), 'Invalid resolvers %s' % resolvers
    
    resolversByContext = {}
    for key, resolver in resolvers.iterate():
        assert isinstance(resolver, IResolver), 'Invalid resolver %s' % resolver
        nameContext, nameAttribute = key

        byContext = resolversByContext.get(nameContext)
        if byContext is None: byContext = resolversByContext[nameContext] = {}
        byContext[nameAttribute] = resolver
        
    return resolversByContext

def asData(context, *classes):
    '''
    Provides the data that is represented in the provided context classes.
    
    @param context: object
        The context object to get the data from.
    @param classes: arguments[ContextMetaClass]
        The context classes to construct the data based on.
    '''
    assert isinstance(context, Context), 'Invalid context %s' % context

    common = set(context.__attributes__)
    for clazz in classes:
        assert isinstance(clazz, ContextMetaClass), 'Invalid context class %s' % clazz
        common.intersection_update(clazz.__attributes__)
        
    data = {}
    for name in common:
        if context.__attributes__[name] in context: data[name] = getattr(context, name)

    return data

def copy(src, dest, *classes):
    '''
    Copies the data from the source context to the destination context based on the provided context classes.
    
    @param context: object
        The context object to get the data from.
    @param classes: arguments[ContextMetaClass]
        The context classes to construct the data based on.
    '''
    assert isinstance(src, Context), 'Invalid source context %s' % src
    assert isinstance(dest, Context), 'Invalid destination context %s' % dest

    common = set(src.__attributes__)
    common.intersection_update(dest.__attributes__)
    for clazz in classes:
        assert isinstance(clazz, ContextMetaClass), 'Invalid context class %s' % clazz
        common.intersection_update(clazz.__attributes__)
        
    for name in common:
        if (name, src.__attributes__[name]) in src: setattr(dest, name, getattr(src, name))
