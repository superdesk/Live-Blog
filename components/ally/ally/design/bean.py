'''
Created on Aug 22, 2012

@package: ally base
@copyright: 2012 Sourcefabric o.p.s.
@license: http://www.gnu.org/licenses/gpl-3.0.txt
@author: Gabriel Nistor

Provides the bean support.
'''

from abc import ABCMeta
from ally.support.util import immut
from inspect import isclass

# --------------------------------------------------------------------

class Attribute:
    '''
    Defines a bean attribute.
    '''
    __slots__ = ('locked', 'types', 'factory', 'default', 'doc', 'name', 'clazz', 'descriptor')

    def __init__(self, *types, default=None, factory=None, doc=None):
        '''
        Construct a bean attribute.
        
        @param types: arguments[class]
            The types of the defined attribute.
        @param default: object
            The default value, this is used if there is not factory provided.
        @param factory: Callable|None
            The factory to create values when there is not value for attribute.
        @keyword doc: string|None
            The documentation associated with the attribute.
        '''
        assert factory is None or callable(factory), 'Invalid factory %s' % factory
        assert doc is None or isinstance(doc, str), 'Invalid documentation %s' % doc
        assert types, 'At least a type is required'
        if __debug__:
            for clazz in types: assert isclass(clazz), 'Invalid class %s' % clazz

        self.locked = False
        self.types = types
        self.factory = factory
        self.default = default
        self.doc = doc

        self.name = None
        self.clazz = None
        self.descriptor = None

    def __setattr__(self, key, value):
        try: locked = self.locked
        except AttributeError: locked = False

        if not locked: object.__setattr__(self, key, value)
        else: raise AttributeError('Immutable attribute')

    # ----------------------------------------------------------------

    def __get__(self, obj, owner=None):
        '''
        Descriptor get.
        '''
        if obj is None: return self
        if self.descriptor:
            try: return self.descriptor.__get__(obj, owner)
            except AttributeError:
                if self.factory is not None:
                    self.__set__(obj, self.factory())
                    return self.descriptor.__get__(obj, owner)
                return self.default
        return obj.__dict__.get(self.name)

    def __set__(self, obj, value):
        '''
        Descriptor set.
        '''
        assert value is None or isinstance(value, self.types), 'Invalid value \'%s\' for %s' % (value, self.types)
        if self.descriptor: self.descriptor.__set__(obj, value)
        else: obj.__dict__[self.name] = value

    def __str__(self):
        return ''.join(self.__class__.__name__, '(', ''.join(type.__name__ for type in self.types), ')')

# --------------------------------------------------------------------

class BeanMetaClass(ABCMeta):
    '''
    Used for the bean objects to behave like a data container only.
    The bean can be checked against any object that has the specified attributes with values of the specified 
    classes instance.
    '''

    def __new__(cls, name, bases, namespace):
        if not bases: return super().__new__(cls, name, bases, namespace)

        attributes = {}
        for key, value in namespace.items():
            if isinstance(value, Attribute): attributes[key] = value

        namespace = {key:value for key, value in namespace.items() if key not in attributes}
        namespace['__slots__'] = tuple(attributes)

        self = super().__new__(cls, name, bases, namespace)

        for key, attribute in attributes.items():
            assert isinstance(attribute, Attribute)
            attribute.name = key
            attribute.clazz = self
            attribute.descriptor = getattr(self, key)
            attribute.locked = True
            setattr(self, key, attribute)

        # Adding also the parent attributes.
        for base in bases:
            if base is Bean: continue
            if isinstance(base, BeanMetaClass):
                assert isinstance(base, BeanMetaClass)
                attributes.update(base.__attributes__)

        self.__attributes__ = immut(attributes)

        return self

class Bean(metaclass=BeanMetaClass):
    '''
    The base bean class, this class is to be inherited by bean classes in order to provide more functionality for
    attributes.
    '''

    def __init__(self, **keyargs):
        for name, value in keyargs.items(): setattr(self, name, value)

    def __contains__(self, attribute):
        if not isinstance(attribute, Attribute): return False
        assert isinstance(attribute, Attribute)
        owned = self.__attributes__.get(attribute.name)
        if owned is None: return False

        try: return isinstance(owned.descriptor.__get__(self), attribute.types)
        except AttributeError: return False

    @classmethod
    def __subclasshook__(cls, C):
        if cls is Bean: return Bean in C.__mro__
        if isinstance(C, BeanMetaClass):
            assert isinstance(C, BeanMetaClass)

            return set(cls.__attributes__).issubset(C.__attributes__)

        return NotImplemented
