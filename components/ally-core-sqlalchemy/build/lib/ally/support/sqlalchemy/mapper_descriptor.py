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

class MappedProperty(Property):
    '''
    Provides the property descriptor that is handling an SQL alchemy descriptor.
    '''
    __slots__ = Property.__slots__ + ('descriptor',)

    def __init__(self, type, descriptor, reference):
        '''
        Construct the mapped property.
        
        @param type: TypeModelProperty
            The property type represented by the mapped property.
        @param descriptor: object
            A descriptor to delegate to.
        @see: Property.__init__
        '''
        assert isinstance(type, TypeModelProperty), 'Invalid type %s' % type
        assert descriptor is not None, 'A descriptor is required'
        assert hasattr(descriptor, '__get__'), 'Invalid descriptor %s, has no __get__' % descriptor
        assert hasattr(descriptor, '__set__'), 'Invalid descriptor %s, has no __set__' % descriptor
        assert hasattr(descriptor, '__delete__'), 'Invalid descriptor %s, has no __delete__' % descriptor

        super().__init__(type, reference)
        self.descriptor = descriptor

    def __get__(self, obj, clazz=None):
        '''
        @see: Property.__get__
        '''
        if obj is None: return super().__get__(obj, clazz)
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
