'''
Created on Jun 12, 2012

@package: utilities
@copyright: 2012 Sourcefabric o.p.s.
@license: http://www.gnu.org/licenses/gpl-3.0.txt
@author: Gabriel Nistor

Provides the context support.
'''

from abc import ABCMeta
from inspect import isclass

# --------------------------------------------------------------------

def defines(*types, doc=None):
    '''
    Construct a defining attribute for the context. The defines attribute means that the context can provide a value
    for the attribute, but is not mandatory also whenever managing an attribute if this type is a good idea to check
    if there aren't already values provided. For a group of contexts a defines attribute can be defined multiple times.
    
    @param types: arguments[class]
        The types of the defined attribute.
    @keyword doc: string
        The documentation associated with the attribute.
    '''
    return Attribute(DEFINED, types, doc)

def optional(*types, doc=None):
    '''
    Construct an optional attribute for the context. The optional attribute means that the context is valid even if
    there is no value for the attribute. The optional can also update or change the value for the attribute.
    
    @param types: arguments[class]
        The types of the optional attribute, the attribute value can be any one of the provided attributes.
    @keyword doc: string
        The documentation associated with the attribute.
    '''
    return Attribute(OPTIONAL, types, doc)

def requires(*types, doc=None):
    '''
    Construct a required attribute for the context. The requires attribute means that the context is valid only if
    there is a value for the attribute, the context should not change the value.
    
    @param types: arguments[class]
        The types of the required attribute, the attribute value can be any one of the provided attributes.
    @param doc: string
        The documentation associated with the attribute.
    '''
    return Attribute(REQUIRED, types, doc)

# --------------------------------------------------------------------

DEFINED = 1 << 1
# Status flag for defined attributes.
REQUIRED = 1 << 2
# Status flag for required attributes.
OPTIONAL = 1 << 3
# Status flag for optional attributes.

class Attribute:
    '''
    Defines a context attribute.
    '''

    def __init__(self, status, types, doc=None):
        '''
        Construct the property.
        
        @param status: integer
            The status of the property.
        @param types: tuple(class)
            The type for the property.
        '''
        assert isinstance(status, int), 'Invalid status %s' % status
        assert isinstance(types, tuple), 'Invalid types %s' % types
        assert types, 'At least a type is required'
        if __debug__:
            for clazz in types: assert isclass(clazz), 'Invalid class %s' % clazz
        assert doc is None or isinstance(doc, str), 'Invalid documentation %s' % doc

        self.status = status
        self.types = types
        self.doc = doc

        self.name = None
        self.descriptor = None

    # ----------------------------------------------------------------

    def __get__(self, obj, owner=None):
        '''
        Descriptor get.
        '''
        if obj is None: return self
        assert self.descriptor is not None, 'No descriptor available %s' % self.descriptor
        return self.descriptor.__get__(obj, owner)

    def __set__(self, obj, value):
        '''
        Descriptor set.
        '''
        assert self.descriptor is not None, 'No descriptor available %s' % self.descriptor
        assert isinstance(value, self.types), 'Invalid value \'%s\' for %s' % (value, self.types)
        self.descriptor.__set__(obj, value)

    def __str__(self):
        status = 'UNKNOWN'
        if self.status & DEFINED: status = 'DEFINES'
        elif self.status & REQUIRED: status = 'REQUIRED'
        elif self.status & OPTIONAL: status = 'OPTIONAL'

        return ''.join((self.__class__.__name__, '(', status, '=' , self.name or '', ':',
                        ','.join(type.__name__ for type in self.types), ')'))

# --------------------------------------------------------------------
ALLOWED = {'__module__', '__doc__'}
# The allowed attributes in a context class.
class ContextMetaClass(ABCMeta):
    '''
    Used for the context objects to behave like a data container only.
    The context can be checked against any object that has the specified attributes with values of the specified 
    classes instance.
    '''

    def __new__(cls, name, bases, namespace):
        if not bases: return super().__new__(cls, name, bases, namespace)
        if bases != (Context,):
            raise TypeError('A context class can only inherit Context, illegal classes %s' % bases)

        attributes = {}
        for key, value in namespace.items():
            if key in ALLOWED: continue
            if not isinstance(value, Attribute):
                raise TypeError('Invalid attribute \'%s\' for name \'%s\'' % (value, key))
            attributes[key] = value

        namespace = {key:value for key, value in namespace.items() if key not in attributes}
        namespace['__slots__'] = tuple(attributes)

        self = super().__new__(cls, name, bases, namespace)

        for key, attribute in attributes.items():
            assert isinstance(attribute, Attribute)
            attribute.name = key
            attribute.descriptor = getattr(self, key)
            setattr(self, key, attribute)

        self.__attributes__ = attributes

        return self

    def __add__(self, other):
        '''
        Composes this context meta with the provided context meta.
        
        @param other: ContextMetaClass
            The other context meta to compose with.
        @return: ContextMetaClass
            The context meta that contains the attributes from this context meta and the provided context meta.
        '''
        assert isinstance(other, ContextMetaClass), 'Invalid other context meta %s' % other
        names = set(self.__attributes__)
        names.update(other.__attributes__)

        attributes = {}
        for name in names:
            attr = self.__attributes__.get(name)
            attro = other.__attributes__.get(name)
            if attr is not None:
                assert isinstance(attr, Attribute), 'Invalid attribute %s' % attr
                if attro is not None:
                    assert isinstance(attro, Attribute), 'Invalid attribute %s' % attro
                    attrnew = combine(attr, attro)
                else: attrnew = Attribute(attr.status, attr.types, doc=attr.doc)
            else: attrnew = Attribute(attro.status, attro.types, doc=attro.doc)

            attributes[name] = attrnew

        return ContextMetaClass('%s+%s' % (self.__name__, other.__name__), (Context,), attributes)


class Context(metaclass=ContextMetaClass):
    '''
    The base context class, this class needs to be inherited by all classes that need to behave like a data context.
    '''
    __slots__ = ()

    @classmethod
    def __subclasshook__(cls, C):
        if cls is Context: return Context in C.__mro__
        if isinstance(C, ContextMetaClass):
            assert isinstance(C, ContextMetaClass)

            for name, attr in cls.__attributes__.items():
                assert isinstance(attr, Attribute)

                if attr.status & OPTIONAL or attr.status & DEFINED: continue
                if name not in C.__attributes__: return False
                oattr = C.__attributes__[name]

                assert isinstance(oattr, Attribute)

                for typ in attr.types:
                    if typ not in oattr.types: return False

            return True
        return NotImplemented

    def __contains__(self, atrr):
        if not isinstance(atrr, Attribute): return False
        assert isinstance(atrr, Attribute)
        try:
            value = getattr(self, atrr.name)
            # Check if the value is of the expected types.
            return isinstance(value, atrr.types)
        except AttributeError: return False

# --------------------------------------------------------------------

def docFrom(attr1, attr2):
    '''
    Combines the documentation of the two attributes.
    
    @param attr1: Attribute
    @param attr2: Attribute
        The attributes to combine the documentation for.
    @return: string|None
        The combined documentation.
    '''
    assert isinstance(attr1, Attribute), 'Invalid attribute %s' % attr1
    assert isinstance(attr2, Attribute), 'Invalid attribute %s' % attr2

    docs = []
    if attr1.doc is not None: docs.append(attr1.doc)
    if attr2.doc is not None: docs.append(attr2.doc)

    if docs: return '\n'.join(docs)

def combine(attr1, attr2):
    '''
    Combines the two attributes in a single one.
    
    @param attr1: Attribute
    @param attr2: Attribute
        The attributes to be combined.
    @return: Attribute
        The combined attribute.
    '''
    assert isinstance(attr1, Attribute), 'Invalid attribute %s' % attr1
    assert isinstance(attr2, Attribute), 'Invalid attribute %s' % attr2

    if attr1.status & DEFINED:
        types = set(attr1.types)
        if attr2.status & DEFINED:
            types.update(attr2.types)
            return Attribute(attr1.status | attr2.status, tuple(types), doc=docFrom(attr1, attr2))

        elif attr2.status & REQUIRED:
            types.intersection_update(attr2.types)
            if not types: raise TypeError('Cannot combine attributes \'%s\' and \'%s\'' % (attr1, attr2))
            return Attribute(attr2.status, tuple(types), doc=docFrom(attr1, attr2))

        else:
            # The second attribute is most likely optional, so is not take in consideration at all
            return Attribute(attr1.status, attr1.types, doc=docFrom(attr1, attr2))

    elif attr2.status & DEFINED:
        return combine(attr2, attr1)

    else:
        # In this case most likely both attributes are optional
        types = set(attr1.types)
        types.update(attr2.types)
        return Attribute(attr1.status | attr2.status, tuple(types), doc=docFrom(attr1, attr2))
