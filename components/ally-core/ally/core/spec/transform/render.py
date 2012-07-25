'''
Created on Jun 27, 2012

@package: ally core
@copyright: 2012 Sourcefabric o.p.s.
@license: http://www.gnu.org/licenses/gpl-3.0.txt
@author: Gabriel Nistor

Provides exploits for transforming object to rendered content. 
'''

from collections import deque
import abc

# --------------------------------------------------------------------

class IRender(metaclass=abc.ABCMeta):
    '''
    The specification for the renderer of encoded objects.
    '''
    __slots__ = ()

    @abc.abstractclassmethod
    def value(self, name, value):
        '''
        Called to signal that a value has to be rendered.

        @param name: string
            The value name.
        @param value: string
            The value.
        '''

    @abc.abstractclassmethod
    def objectStart(self, name, attributes=None):
        '''
        Called to signal that an object has to be rendered.
        
        @param name: string
            The object name.
        @param attributes: dictionary{string, string}|None
            The attributes for the value.
        '''

    @abc.abstractclassmethod
    def objectEnd(self):
        '''
        Called to signal that the current object has ended the rendering.
        '''

    @abc.abstractclassmethod
    def collectionStart(self, name, attributes=None):
        '''
        Called to signal that a collection has to be rendered.
        
        @param name: string
            The collection name.
        @param attributes: dictionary{string, string}|None
            The attributes for the collection.
        '''

    @abc.abstractclassmethod
    def collectionEnd(self):
        '''
        Called to signal that the current collection has ended the rendering.
        '''

class Value:
    '''
    Container for the text value.
    '''
    __slots__ = ('name', 'value')

    def __init__(self, name, value):
        '''
        Construct the text value.
        
        @param name: string
            The name for the value.
        @param value: string
            The value.
        '''
        assert isinstance(name, str), 'Invalid name %s' % name
        assert isinstance(value, str), 'Invalid value %s' % value

        self.name = name
        self.value = value

class Object:
    '''
    Container for a text object.
    '''
    __slots__ = ('name', 'properties', 'attributes')

    def __init__(self, name, *properties, attributes=None):
        '''
        Construct the text object.
        '''
        assert isinstance(name, str), 'Invalid name %s' % name
        assert attributes is None or isinstance(attributes, dict), 'Invalid attributes %s' % attributes

        self.name = name
        self.properties = properties
        self.attributes = attributes

class List:
    '''
    Container for a text collection.
    '''
    __slots__ = ('name', 'items', 'attributes')

    def __init__(self, name, *items, attributes=None):
        '''
        Construct the text list.
        '''
        assert isinstance(name, str), 'Invalid name %s' % name
        assert attributes is None or isinstance(attributes, dict), 'Invalid attributes %s' % attributes

        self.name = name
        self.items = items
        self.attributes = attributes

# --------------------------------------------------------------------

class RenderToObject(IRender):
    '''
    A @see: IRender implementation that captures the data into a text object.
    '''
    __slots__ = ('obj', 'processing')

    def __init__(self):
        '''
        Construct the render.
        '''
        self.obj = None
        self.processing = deque()

    def value(self, name, value):
        '''
        @see: IRender.value
        '''
        assert self.processing, 'No object available to place the value'
        assert isinstance(name, str), 'Invalid name %s' % name
        assert isinstance(value, str), 'Invalid value %s' % value

        obj = self.processing[0]
        if isinstance(obj, dict): obj[name] = value
        else: obj.append(value)

    def objectStart(self, name, attributes=None):
        '''
        @see: IRender.objectStart
        '''
        assert isinstance(name, str), 'Invalid name %s' % name
        assert attributes is None or isinstance(attributes, dict), 'Invalid attributes %s' % attributes

        value = {}
        if attributes:
            for attrName, attrValue in attributes.items():
                assert isinstance(attrName, str), 'Invalid attribute name %s' % attrName
                assert isinstance(attrValue, str), 'Invalid attribute value %s' % attrValue
            value.update(attributes)

        if self.processing:
            obj = self.processing[0]
            if isinstance(obj, dict): obj[name] = value
            else: obj.append(value)

        if not self.processing: self.obj = value
        self.processing.appendleft(value)

    def objectEnd(self):
        '''
        @see: IRender.objectEnd
        '''
        assert self.processing and isinstance(self.processing[0], dict), 'No object available to end'

        self.processing.popleft()

    def collectionStart(self, name, attributes=None):
        '''
        @see: IRender.collectionStart
        '''
        assert isinstance(name, str), 'Invalid name %s' % name
        assert attributes is None or isinstance(attributes, dict), 'Invalid attributes %s' % attributes

        valueObj = {}
        if attributes:
            for attrName, attrValue in attributes.items():
                assert isinstance(attrName, str), 'Invalid attribute name %s' % attrName
                assert isinstance(attrValue, str), 'Invalid attribute value %s' % attrValue
            valueObj.update(attributes)

        value = valueObj[name] = []
        if self.processing:
            obj = self.processing[0]
            if isinstance(obj, dict): obj[name] = valueObj
            else: obj.append(valueObj)
        if not self.processing: self.obj = valueObj
        self.processing.appendleft(value)

    def collectionEnd(self):
        '''
        @see: IRender.collectionEnd
        '''
        assert self.processing and isinstance(self.processing[0], list), 'No collection available to end'

        self.processing.popleft()

def renderObject(txt, render):
    '''
    Renders the text object on to the provided renderer.
    
    @param txt: Value, Object, List
        The text object to render.
    @param renderer: IRender
        The renderer to render to.
    '''
    assert isinstance(render, IRender), 'Invalid render %s' % render

    if isinstance(txt, Value):
        assert isinstance(txt, Value)

        render.value(txt.name, txt.value)

    elif isinstance(txt, Object):
        assert isinstance(txt, Object)

        render.objectStart(txt.name, txt.attributes)
        for prop in txt.properties: renderObject(prop, render)
        render.objectEnd()

    elif isinstance(txt, List):
        assert isinstance(txt, List)

        render.collectionStart(txt.name, txt.attributes)
        for item in txt.items: renderObject(item, render)
        render.collectionEnd()

    else: raise ValueError('Invalid text object %s' % txt)
