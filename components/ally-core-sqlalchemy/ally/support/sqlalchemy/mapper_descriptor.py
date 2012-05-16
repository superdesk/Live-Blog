'''
Created on Mar 27, 2012

@package: ally core sql alchemy
@copyright: 2012 Sourcefabric o.p.s.
@license: http://www.gnu.org/licenses/gpl-3.0.txt
@author: Gabriel Nistor

Provides the descriptors of REST models for the SQL alchemy mappings.
'''

from abc import ABCMeta
from ally.api.operator.descriptor import Property
from ally.api.operator.type import TypeModelProperty
from sqlalchemy.orm.mapper import Mapper
from sqlalchemy.orm.attributes import InstrumentedAttribute

# --------------------------------------------------------------------

class MappedSupportMeta(ABCMeta):
    '''
    Meta class for mapping support that allows for instance check base on the '_ally_mapping' attribute.
    '''

    def __instancecheck__(self, instance):
        '''
        @see: ABCMeta.__instancecheck__
        '''
        if ABCMeta.__instancecheck__(self, instance): return True
        return isinstance(getattr(instance, '_ally_mapping', None), Mapper)

class MappedSupport(metaclass=MappedSupportMeta):
    '''
    Support class for mapped classes.
    '''
    _ally_mapping = Mapper # Contains the mapper that represents the model

# --------------------------------------------------------------------
#
#class MappedReference(InstrumentedAttribute, TypeSupport):
#    '''
#    Provides the mapped property reference.
#    @see: Reference
#    '''
#
#    __slots__ = TypeSupport.__slots__ + ('_ally_ref_parent', '_ally_instrumented')
#
#    def __init__(self, type, instrumented, parent=None):
#        '''
#        Constructs the container property descriptor.
#        
#        @param type: TypeModelProperty
#            The property type represented by the mapped reference.
#        '''
#        assert isinstance(type, TypeModelProperty), 'Invalid type %s' % type
#        assert parent is None or isinstance(parent, TypeSupport), \
#        'Invalid parent %s, needs to be a type support' % parent
#        assert isinstance(instrumented, InstrumentedAttribute), 'Invalid instrumented attribute %s' % instrumented
#        TypeSupport.__init__(self, type)
#
#        self._ally_ref_parent = parent
#        self._ally_instrumented = instrumented
#
#    def __getattr__(self, name):
#        '''
#        Provides the contained container properties.
#        
#        @param name: string
#            The property to get from the contained container.
#        '''
#        assert isinstance(name, str), 'Invalid name %s' % name
#        try:
#            return getattr(self._ally_instrumented, name)
#        except AttributeError:
#            typ = self._ally_type.type
#            if isinstance(typ, TypeContainer):
#                assert isinstance(typ, TypeContainer)
#                return MappedReference(typ.childTypeFor(name), self._ally_instrumented, self)
#
#    def adapted(self, adapter):
#        '''
#        @see: InstrumentedAttribute.adapted
#        We need to adjust this in order to be able to alias the REST mapped classes.
#        '''
#        instrumented = self._ally_instrumented.adapted(adapter)
#        adapted = self.__class__(self._ally_type, instrumented, self._ally_ref_parent)
#        adapted.comparator = self.comparator.adapted(adapter)
#        adapted.class_ = self.class_
#        return adapted
#
#    def __repr__(self):
#        r = []
#        if self._ally_ref_parent:
#            r.append(str(self._ally_ref_parent))
#            r.append('->')
#        r.append(str(self._ally_type))
#        r.append('(')
#        r.append(str(self._ally_type.type))
#        r.append(')')
#        return ''.join(r)

class MappedProperty(Property):
    '''
    Provides the property descriptor that is handling an SQL alchemy descriptor.
    '''
    __slots__ = Property.__slots__ + ('typeReference', 'descriptor')

    def __init__(self, type, typeReference, descriptor):
        '''
        Construct the mapped property.
        
        @param type: TypeModelProperty
            The property type represented by the mapped property.
        @param typeReference: TypeModelProperty
            The property reference type.
        @param descriptor: object
            A descriptor to delegate to.
        @see: Property.__init__
        '''
        assert isinstance(type, TypeModelProperty), 'Invalid type %s' % type
        assert isinstance(typeReference, TypeModelProperty), 'Invalid type %s' % typeReference
        assert descriptor is not None, 'A descriptor is required'
        assert hasattr(descriptor, '__get__'), 'Invalid descriptor %s, has no __get__' % descriptor
        assert hasattr(descriptor, '__set__'), 'Invalid descriptor %s, has no __set__' % descriptor
        assert hasattr(descriptor, '__delete__'), 'Invalid descriptor %s, has no __delete__' % descriptor

        super().__init__(type)
        self.typeReference = typeReference
        self.descriptor = descriptor

    def __get__(self, obj, clazz=None):
        '''
        @see: Property.__get__
        '''
        if obj is None:
            assert self.type.parent.isOf(clazz), 'Illegal class %s, expected %s' % (clazz, self.type.parent)
            value = self.descriptor.__get__(None, clazz)
            if value is not None:
                try: value._ally_type = self.typeReference
                except AttributeError: pass
            return value
        return self.descriptor.__get__(obj, clazz)

    def __contained__(self, obj):
        '''
        A mapped property is always contained.
        @see: Property.__contained__
        '''
        return True

    def __set__(self, obj, value):
        '''
        @see: Property.__set__
        '''
        self.descriptor.__set__(obj, value)

    def __delete__(self, obj):
        '''
        @see: Property.__delete__
        '''
        self.descriptor.__delete__(obj)

# --------------------------------------------------------------------
#TODO: check if is still a problem in the new SQL alchemy version
# This is a fix for the aliased models.
def adapted(self, adapter):
    '''
    @see: InstrumentedAttribute.adapted
    We need to adjust this in order to be able to alias.
    '''
    adapted = InstrumentedAttribute(self.prop, self.mapper, adapter)
    adapted.comparator = self.comparator.adapted(adapter)
    adapted.class_ = self.class_
    return adapted
InstrumentedAttribute.adapted = adapted
