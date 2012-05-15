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
from ally.api.operator.type import TypeContainer, TypeModelProperty
from ally.api.type import TypeSupport
from sqlalchemy.orm.attributes import InstrumentedAttribute
from sqlalchemy.orm.mapper import Mapper

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

class MappedReference(InstrumentedAttribute, TypeSupport):
    '''
    Provides the mapped property reference.
    @see: Reference
    '''

    __slots__ = TypeSupport.__slots__ + ('_ally_ref_parent', '_ally_instrumented')

    def __init__(self, type, instrumented, parent=None):
        '''
        Constructs the container property descriptor.
        
        @param type: TypeModelProperty
            The property type represented by the mapped reference.
        '''
        assert isinstance(type, TypeModelProperty), 'Invalid type %s' % type
        assert parent is None or isinstance(parent, TypeSupport), \
        'Invalid parent %s, needs to be a type support' % parent
        assert isinstance(instrumented, InstrumentedAttribute), 'Invalid instrumented attribute %s' % instrumented
        TypeSupport.__init__(self, type)

        self._ally_ref_parent = parent
        self._ally_instrumented = instrumented

    def __getattr__(self, name):
        '''
        Provides the contained container properties.
        
        @param name: string
            The property to get from the contained container.
        '''
        assert isinstance(name, str), 'Invalid name %s' % name
        try:
            return getattr(self._ally_instrumented, name)
        except AttributeError:
            typ = self._ally_type.type
            if isinstance(typ, TypeContainer):
                assert isinstance(typ, TypeContainer)
                return MappedReference(typ.childTypeFor(name), self._ally_instrumented, self)

    def adapted(self, adapter):
        '''
        @see: InstrumentedAttribute.adapted
        We need to adjust this in order to be able to alias the REST mapped classes.
        '''
        instrumented = self._ally_instrumented.adapted(adapter)
        adapted = self.__class__(self._ally_type, instrumented, self._ally_ref_parent)
        adapted.comparator = self.comparator.adapted(adapter)
        adapted.class_ = self.class_
        return adapted

    def __repr__(self):
        r = []
        if self._ally_ref_parent:
            r.append(str(self._ally_ref_parent))
            r.append('->')
        r.append(str(self._ally_type))
        r.append('(')
        r.append(str(self._ally_type.type))
        r.append(')')
        return ''.join(r)

class MappedProperty(Property):
    '''
    Provides the property descriptor that is handling an SQL alchemy mapped column.
    '''
    __slots__ = Property.__slots__ + ('__set__', '__delete__')

    def __init__(self, type, reference, instrumented):
        '''
        Construct the mapped property.
        
        @param type: TypeModelProperty
            The property type represented by the mapped property.
        @see: Property.__init__
        '''
        assert isinstance(type, TypeModelProperty), 'Invalid type %s' % type
        assert isinstance(instrumented, InstrumentedAttribute), 'Invalid instrumented attribute %s' % instrumented
        Property.__init__(self, type, reference)
        self.__set__ = instrumented.__set__
        self.__delete__ = instrumented.__delete__
