'''
Created on Jul 27, 2012

@package: ally core
@copyright: 2012 Sourcefabric o.p.s.
@license: http://www.gnu.org/licenses/gpl-3.0.txt
@author: Gabriel Nistor

Provides basic encode implementations. 
'''

from ally.api.operator.container import Container
from ally.api.operator.type import TypeExtension
from ally.api.type import typeFor, Type, Iter
from ally.core.spec.encdec.exploit import IResolve, ResolveError
from ally.core.spec.encdec.render import IRender
from ally.core.spec.resources import Normalizer, Converter
from collections import Iterable, OrderedDict
from inspect import isfunction, ismethod

# --------------------------------------------------------------------

class EncodeObject:
    '''
    Exploit for object encoding.
    '''
    __slots__ = ('name', 'getter', 'properties')

    def __init__(self, name, getter=None):
        '''
        Create a encode exploit for a model.
        
        @param name: string
            The name of the model to encode.
        @param getter: callable(object) -> object|None
            The getter used to get the object from the value object.
        '''
        assert isinstance(name, str), 'Invalid name %s' % name
        assert getter is None or callable(getter), 'Invalid getter %s' % getter

        self.name = name
        self.getter = getter
        self.properties = OrderedDict()

    def __call__(self, value, render, normalizer, name=None, **data):
        assert isinstance(normalizer, Normalizer), 'Invalid normalizer %s' % normalizer
        assert isinstance(render, IRender), 'Invalid render %s' % render
        assert name is None or isinstance(name, str), 'Invalid name %s' % name

        if self.getter: value = self.getter(value)
        if value is None: return

        render.objectStart(normalizer.normalize(name or self.name))
        data.update(value=value, render=render, normalizer=normalizer)
        for nameProp, encodeProp in self.properties.items():
            try:
                encodeProp(name=nameProp, **data)
            except:
                self.handleError(encodeProp)

        render.objectEnd()

    def handleError(self, exploit):
        '''
        Handles the error for the provided exploit.
        '''
        if isfunction(exploit) or ismethod(exploit):
            cd = exploit.__code__
            raise ResolveError('Problems with exploit at:\n  File "%s", line %i, in %s' %
                               (cd.co_filename, cd.co_firstlineno, exploit.__name__))
        else: raise ResolveError('Problems with exploit call %s' % exploit)

class EncodeCollection:
    '''
    Exploit for collection encoding.
    '''
    __slots__ = ('name', 'exploitItem', 'getter')

    def __init__(self, name, exploitItem, getter=None):
        '''
        Create a encode exploit for a collection.
        
        @param name: string
            The name to use for the collection.
        @param exploitItem: callable(**data)
            The exploit to be used for the item encoding.
        @param getter: callable(object) -> object|None
            The getter used to get the model collection from the value object.
        '''
        assert isinstance(name, str), 'Invalid name %s' % name
        assert callable(exploitItem), 'Invalid exploit %s' % exploitItem
        assert getter is None or callable(getter), 'Invalid getter %s' % getter

        self.name = name
        self.exploitItem = exploitItem
        self.getter = getter

    def __call__(self, value, normalizer, converter, render, resolve, name=None, **data):
        assert isinstance(normalizer, Normalizer), 'Invalid normalizer %s' % normalizer
        assert isinstance(converter, Converter), 'Invalid converter %s' % converter
        assert isinstance(render, IRender), 'Invalid render %s' % render
        assert isinstance(resolve, IResolve), 'Invalid resolve %s' % resolve

        if self.getter: value = self.getter(value)
        if value is None: return
        assert isinstance(value, Iterable), 'Invalid value %s' % value

        typeValue = typeFor(value)
        if typeValue and isinstance(typeValue, TypeExtension):
            assert isinstance(typeValue, TypeExtension)
            assert isinstance(typeValue.container, Container)
            attrs = {}
            for prop, propType in typeValue.container.properties.items():
                propValue = getattr(value, prop)
                if propValue is not None: attrs[normalizer.normalize(prop)] = converter.asString(propValue, propType)
        else: attrs = None

        data.update(normalizer=normalizer, converter=converter, render=render, resolve=resolve)
        render.collectionStart(normalizer.normalize(name or self.name), attrs)
        resolve.queueBatch(self.exploitItem, (dict(data, value=item) for item in value))
        resolve.queue(self.finalize, render=render)

    def finalize(self, render, **data):
        assert isinstance(render, IRender), 'Invalid render %s' % render

        render.collectionEnd()

class EncodePrimitive:
    '''
    Exploit for primitive encoding.
    '''
    __slots__ = ('typeValue', 'getter')

    def __init__(self, typeValue, getter=None):
        '''
        Create a encode exploit for a primitive property also encodes primitive value list.
        
        @param typeValue: Type
            The type of the property value to encode.
        @param getter: callable(object) -> object|None
            The getter used to get the value from the value object, if None provided it will use the received value.
        @return: callable(**data)
            The exploit that provides the primitive encoding.
        '''
        assert isinstance(typeValue, Type), 'Invalid property value type %s' % typeValue
        assert getter is None or callable(getter), 'Invalid getter %s' % getter

        self.typeValue = typeValue
        self.getter = getter

    def __call__(self, name, value, render, normalizer, converter, **data):
        assert isinstance(name, str), 'Invalid name %s' % name
        assert isinstance(render, IRender), 'Invalid render %s' % render
        assert isinstance(normalizer, Normalizer), 'Invalid normalizer %s' % normalizer
        assert isinstance(converter, Converter), 'Invalid converter %s' % converter

        if self.getter: value = self.getter(value)
        if value is None: return
        if isinstance(self.typeValue, Iter):
            assert isinstance(value, Iterable), 'Invalid value %s' % value

            render.collectionStart(name)
            nameValue = normalizer.normalize(self.nameValue)
            for item in value:
                render.value(nameValue, converter.asString(item, self.typeValue.itemType))
            render.collectionEnd()
        else:
            render.value(name, converter.asString(value, self.typeValue))

class EncodeId(EncodePrimitive):
    '''
    Exploit for id encoding.
    '''
    __slots__ = ()

    def __call__(self, name, value, render, converterId, **data):
        assert isinstance(name, str), 'Invalid name %s' % name
        assert isinstance(render, IRender), 'Invalid render %s' % render
        assert isinstance(converterId, Converter), 'Invalid converter id %s' % converterId

        if self.getter: value = self.getter(value)
        if value is None: return
        render.value(name, converterId.asString(value, self.typeValue))
