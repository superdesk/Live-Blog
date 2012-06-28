'''
Created on Jun 27, 2012

@package: ally core
@copyright: 2012 Sourcefabric o.p.s.
@license: http://www.gnu.org/licenses/gpl-3.0.txt
@author: Gabriel Nistor

Provides exploits for transforming object to rendered content. 
'''

from ally.api.type import Type
from ally.core.spec.resources import Converter, Normalizer
from ally.design.exploit import IResolve
from ally.support.util import immut
from collections import Iterable, deque
import abc

# --------------------------------------------------------------------

SAMPLE = object() # Marker used to instruct the encoders to provide a sample.

# --------------------------------------------------------------------

class IRender(metaclass=abc.ABCMeta):
    '''
    The specification for the renderer of encoded objects.
    '''
    __slots__ = ()

    @abc.abstractclassmethod
    def value(self, value, name=None, attributes=None):
        '''
        Called to signal that a value has to be rendered.
        
        @param value: string
            The value.
        @param name: string|None
            The value name.
        @param attributes: dictionary{string, string}|None
            The attributes for the value.
        '''

    @abc.abstractclassmethod
    def objectStart(self, name=None):
        '''
        Called to signal that an object has to be rendered.
        
        @param name: string|None
            The object name.
        '''

    @abc.abstractclassmethod
    def objectEnd(self):
        '''
        Called to signal that the current object has ended the rendering.
        '''

    @abc.abstractclassmethod
    def collectionStart(self, name=None, attributes=None):
        '''
        Called to signal that a collection has to be rendered.
        
        @param name: string|None
            The collection name.
        @param attributes: dictionary{string, string}|None
            The attributes for the collection.
        '''

    @abc.abstractclassmethod
    def collectionEnd(self):
        '''
        Called to signal that the current collection has ended the rendering.
        '''

class RenderCapture(IRender, deque):
    '''
    A @see: IRender implementation that just captures the render events.
    '''
    __slots__ = ()

    def value(self, value, name=None, attributes=None):
        '''
        @see: IRender.value
        '''
        assert isinstance(value, str), 'Invalid value %s' % value
        assert name is None or isinstance(name, str), 'Invalid name %s' % name
        assert attributes is None or isinstance(attributes, dict), 'Invalid attributes %s' % attributes
        if __debug__:
            if attributes:
                for attrName, attrValue in attributes.items():
                    assert isinstance(attrName, str), 'Invalid attribute name %s' % attrName
                    assert isinstance(attrValue, str), 'Invalid attribute value %s' % attrValue

        self.append(('value', (name, value, attributes)))

    def objectStart(self, name=None):
        '''
        @see: IRender.objectStart
        '''
        assert name is None or isinstance(name, str), 'Invalid name %s' % name

        self.append(('objectStart', (name,)))

    def objectEnd(self):
        '''
        @see: IRender.objectEnd
        '''
        self.append(('objectEnd', ()))

    def collectionStart(self, name=None, attributes=None):
        '''
        @see: IRender.collectionStart
        '''
        assert name is None or isinstance(name, str), 'Invalid name %s' % name
        assert attributes is None or isinstance(attributes, dict), 'Invalid attributes %s' % attributes
        if __debug__:
            if attributes:
                for attrName, attrValue in attributes.items():
                    assert isinstance(attrName, str), 'Invalid attribute name %s' % attrName
                    assert isinstance(attrValue, str), 'Invalid attribute value %s' % attrValue

        self.append(('collectionStart', (name, attributes)))

    def collectionEnd(self):
        '''
        @see: IRender.collectionEnd
        '''
        self.append(('collectionEnd', ()))

# --------------------------------------------------------------------

def renderConverted(type):
    '''
    Exploit that renders a value after it has been converted.
    
    @param type: Type
        The type used for conversion.
    @param pathItem: object
        The path of the item that is used for rendering the values from the collection.
    '''
    assert isinstance(type, Type), 'Invalid type %s' % type

    def exploit(value, render, converter, name=None, **data):
        assert isinstance(render, IRender), 'Invalid render %s' % render
        assert isinstance(converter, Converter), 'Invalid converter %s' % converter

        if value is SAMPLE: value = 'a %s value' % type
        else: value = converter.asString(value, type)

        render.value(value, name)

        return True
    return exploit

def renderCollection(pathItem):
    '''
    Exploit that renders the value collection, when this exploit is reached the value has to be iterable.
    
    @param pathItem: object
        The path of the item that is used for rendering the values from the collection.
    '''
    def exploit(name=None, value=None, render=None, resolve=None, start=True, **data):
        if start:
            if value is SAMPLE: value = (SAMPLE,)
            assert isinstance(value, Iterable), 'Invalid value %s' % value
            assert isinstance(render, IRender), 'Invalid render %s' % render
            assert isinstance(resolve, IResolve), 'Invalid resolve %s' % resolve

            render.collectionStart(name)
            dataItem = (dict(data, value=item, render=render, resolve=resolve) for item in value)
            if not resolve.requestBatch(pathItem, data=dataItem): return False
            if not resolve.request(start=False): return False
        else: render.collectionEnd()

        return True
    return exploit

def renderJoin(delegate, separator, separatorEscape=None):
    '''
    Exploit that joins the collection rendered by the delegate. The collection needs to be of values and not objects.
    
    @param delegate: callable(**data)
        The exploit call to delegate for rendering the collection to be joined.
    @param separator: string
        The separator to use to join the values.
    @param separatorEscape: string|None
        The value to use in escaping the separator string in the value items.
    '''
    assert callable(delegate), 'Invalid delegate %s' % delegate
    assert isinstance(separator, str), 'Invalid separator %s' % separator
    assert separatorEscape is None or isinstance(separatorEscape, str), 'Invalid separator escape %s' % separatorEscape

    def exploit(render, resolve, **data):
        assert isinstance(render, IRender), 'Invalid render %s' % render
        assert isinstance(resolve, IResolve), 'Invalid resolve %s' % resolve

        capture = RenderCapture()
        if not delegate(render=capture, **data): return False
        if not resolve.doAll(): return False

        # We now need to take the capture and join it.
        method, args = capture.pop()
        assert method == 'collectionStart', 'Expected a collection rendering, got first method \'%s\'' % method
        name, attributes = args
        assert not attributes, 'No attributes expected for \'%s\' got %s' % (method, attributes)

        items = deque()
        while capture:
            method, args = capture.pop()
            if method == 'collectionEnd': break
            assert method == 'value', 'Expected a value rendering, got method in collection as \'%s\'' % method
            value, _name, attributes = args
            assert not attributes, 'No attributes expected for \'%s\' got %s' % (method, attributes)
            items.append(value)
        else: assert False, 'Unexpected end of captured collection'
        assert not capture, 'Unused captures (%s)' % (','.join(method for method, args in capture))

        if separatorEscape is None: value = separator.join(items)
        else: value = separator.join(item.replace(separator, separatorEscape) for item in items)
        render.value(value, name)

        return True
    return exploit

# --------------------------------------------------------------------

def valueGetter(delegate, getter):
    '''
    Exploit that actually just uses a getter to fetch a value from the value object and pass it to the exploit
    delegate. If the value fetched is None then this exploit will return False and not delegate to the delegated exploit.
    
    @param delegate: callable(**data)
        The exploit call to delegate with the obtained value.
    @param getter: callable(object)
        The getter used to fetch the value from the value object.
    '''
    assert callable(delegate), 'Invalid delegate %s' % delegate
    assert callable(getter), 'Invalid getter %s' % getter

    def exploit(value, **data):
        value = getter(value)
        if value is None: return False
        return delegate(value=value, **data)
    return exploit

def placeName(delegate, name):
    '''
    Exploit that just sets a normalized name as data.
    
    @param delegate: callable(**data)
        The exploit call to delegate with the placed name.
    @param name: string
        The name to place in data.
    '''
    assert callable(delegate), 'Invalid delegate %s' % delegate
    assert isinstance(name, str), 'Invalid name %s' % name

    def exploit(normalizer, **data):
        assert isinstance(normalizer, Normalizer), 'Invalid normalizer %s' % normalizer

        return delegate(name=normalizer.normalize(name), **data)
    return exploit

def placeNameAndGetter(delegate, getter, name):
    '''
    Exploit that combines @see: placeNormazliedName and @see: valueGetter.
    
    @param delegate: callable(**data)
        The exploit call to delegate with the placed name.
    @param getter: callable(object)
        The getter used to fetch the value from the value object.
    @param name: string
        The name to place in data.
    '''
    assert callable(delegate), 'Invalid delegate %s' % delegate
    assert isinstance(name, str), 'Invalid name %s' % name

    def exploit(value, normalizer, **data):
        assert isinstance(normalizer, Normalizer), 'Invalid normalizer %s' % normalizer

        value = getter(value)
        if value is None: return False
        return delegate(name=normalizer.normalize(name), value=value, **data)
    return exploit
