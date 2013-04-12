'''
Created on Mar 13, 2012

@package: ally core sql alchemy
@copyright: 2012 Sourcefabric o.p.s.
@license: http://www.gnu.org/licenses/gpl-3.0.txt
@author: Gabriel Nistor

Provides the descriptors for the mapped attributes.
'''

from ally.api.operator.descriptor import ContainerSupport
from ally.api.operator.type import TypeProperty
from ally.api.type import TypeSupport
from ally.support.util_spec import IContained, IGet
from sqlalchemy.ext.associationproxy import AssociationProxy
from sqlalchemy.ext.hybrid import hybrid_property
from sqlalchemy.orm.attributes import InstrumentedAttribute

# --------------------------------------------------------------------

OWNED_PROPERTY_PROXY = set(('_ally_type', '_ally_proxied', '__get__', '__contained__'))
class PropertyMappingProxy(TypeSupport, IGet, IContained):
    '''
    Property that acts like a proxy for other descriptors.
    '''

    def __init__(self, type, proxied):
        '''
        Construct the mapped instrumented attribute.
        
        @param type: TypeProperty
            The property type represented by the property.
        @param proxied: object
            A proxied object to delegate to.
        '''
        assert isinstance(type, TypeProperty), 'Invalid property type %s' % type
        TypeSupport.__init__(self, type)
        if isinstance(proxied, PropertyMappingProxy): proxied = proxied._ally_proxied

        self._ally_proxied = proxied

    def __getattribute__(self, key):
        if key in OWNED_PROPERTY_PROXY: return object.__getattribute__(self, key)
        return getattr(self._ally_proxied, key)

    def __setattr__(self, key, value):
        if key in OWNED_PROPERTY_PROXY: object.__setattr__(self, key, value)
        else: setattr(self._ally_proxied, key, value)

# --------------------------------------------------------------------

class PropertyAttribute(PropertyMappingProxy, InstrumentedAttribute):
    '''
    Provides the property descriptor for the instrumented attribute.
    '''

    def __init__(self, type, attribute):
        '''
        Construct the mapped instrumented attribute.
        
        @param type: TypeProperty
            The property type represented by the property.
        @param attribute: InstrumentedAttribute
            A instrumented attribute to delegate to.
        '''
        assert isinstance(type, TypeProperty), 'Invalid property type %s' % type
        assert isinstance(attribute, InstrumentedAttribute), 'Invalid attribute %s' % attribute
        PropertyMappingProxy.__init__(self, type, attribute)

    def __get__(self, obj, clazz=None):
        '''
        @see: InstrumentedAttribute.__get__
        '''
        if obj is None: return self
        assert isinstance(obj, ContainerSupport), 'Invalid container object %s' % obj
        assert self._ally_type.parent.isValid(obj), \
        'Invalid container object %s, expected %s' % (obj, self._ally_type.parent)
        return obj._ally_values.get(self._ally_type.property)

    def __contained__(self, obj):
        '''
        @see: IContained.__contained__
        '''
        assert isinstance(obj, ContainerSupport), 'Invalid container object %s' % obj
        assert self._ally_type.parent.isValid(obj), \
        'Invalid container object %s, expected %s' % (obj, self._ally_type.parent)
        return self._ally_type.property in obj._ally_values

class PropertyHybrid(PropertyMappingProxy, hybrid_property):
    '''
    Provides the property descriptor for the hybrid property.
    '''

    def __init__(self, type, hybrid):
        '''
        Construct the hybrid property.
        
        @param type: TypeProperty
            The property type represented by the property.
        @param hybrid: hybrid_property
            The hybrid property to use.
        '''
        assert isinstance(hybrid, hybrid_property), 'Invalid hybrid property %s' % hybrid
        PropertyMappingProxy.__init__(self, type, hybrid)

    def __get__(self, instance, owner):
        '''
        @see: hybrid_property.__get__
        '''
        if instance is None:
            expr = self._ally_proxied.__get__(instance, owner)
            if isinstance(expr, TypeSupport):
                assert isinstance(expr, TypeSupport)
                expr._ally_type == self._ally_type, 'Invalid expression %s has already assigned a different type %s' % (expr, expr._ally_type)
            else: expr._ally_type = self._ally_type
            return expr
        else:
            return self.fget(instance)

    def __contained__(self, obj):
        '''
        @see: IContained.__contained__
        '''
        return True

class PropertyAssociation(PropertyMappingProxy, AssociationProxy):
    '''
    Provides the property descriptor for the instrumented attribute.
    '''

    def __init__(self, type, association):
        '''
        Construct the mapped instrumented attribute.
        
        @param type: TypeProperty
            The property type represented by the property.
        @param attribute: InstrumentedAttribute
            A instrumented attribute to delegate to.
        '''
        assert isinstance(type, TypeProperty), 'Invalid property type %s' % type
        assert isinstance(association, AssociationProxy), 'Invalid association proxy %s' % association
        PropertyMappingProxy.__init__(self, type, association)

    def __get__(self, obj, clazz=None):
        '''
        @see: AssociationProxy.__get__
        '''
        if obj is None: return self
        return self._ally_proxied.__get__(obj, clazz)

    def __contained__(self, obj):
        '''
        @see: IContained.__contained__
        '''
        return True
