'''
Created on May 23, 2012

@package: ally core
@copyright: 2012 Sourcefabric o.p.s.
@license: http://www.gnu.org/licenses/gpl-3.0.txt
@author: Gabriel Nistor

Provides basic meta encode implementations. 
'''

from ally.core.spec.meta import MetaEncode, Value, Collection, Object
from ally.core.impl.meta.general import WithGetter, ContextParse
from ally.api.type import Type
from ally.core.spec.resources import Converter
from functools import reduce

# --------------------------------------------------------------------

class EncodeGet(MetaEncode, WithGetter):
    '''
    An encode that actually just uses a getter to fetch a value from the object and pass it to the contained encoder.
    If the value fetched is None than this encode will return None and not delegate to the contained encoder.
    '''

    def __init__(self, getter, encoder):
        '''
        Construct the get encoder.
        @see: WithGetter.__init__
        
        @param encoder: MetaEncode
            The meta encode to delegate with the obtained value.
        '''
        assert isinstance(encoder, MetaEncode), 'Invalid encoder %s' % encoder
        WithGetter.__init__(self, getter)

        self.encoder = encoder

    def encode(self, obj, context):
        '''
        MetaEncode.encode
        '''
        value = self.getter(obj)
        if value is not None: return self.encoder.encode(value, context)

class EncodeValue(MetaEncode):
    '''
    Encodes the object to a string value by using the converter.
    '''

    def __init__(self, type, identifier=None):
        '''
        Construct the type based encoder.
        
        @param type: Type
            The type represented by the encoder.
        @param identifier: object|None
            The identifier of the encoded value.
        '''
        assert isinstance(type, Type), 'Invalid type %s' % type

        self.type = type
        self.identifier = identifier

    def encode(self, obj, context):
        '''
        MetaEncode.encode
        '''
        assert isinstance(context, ContextParse), 'Invalid context %s' % context
        assert isinstance(context.converter, Converter)

        value = context.converter.asString(obj, self.type)
        return Value(identifier=self.identifier, value=value)

class EncodeObject(MetaEncode):
    '''
    Provides support for encoding an object.
    '''

    def __init__(self, identifier=None):
        '''
        Construct the object encoder.
        
        @param identifier: object|None
            The identifier of the encoded collection.
        
        @ivar properties: list[MetaEncode]
            The meta encode for the object properties.
        @ivar attributes: list[MetaEncode]
            The meta encode for the object attributes.
        '''
        self.identifier = identifier
        self.properties = []
        self.attributes = []

    def encode(self, obj, context):
        '''
        MetaEncode.encode
        '''
        return Object(identifier=self.identifier, value=obj, properties=self.properties, attributes=self.attributes)

class EncodeCollection(MetaEncode):
    '''
    Provides support for encoding a collection.
    '''

    def __init__(self, item, identifier=None):
        '''
        Construct the collection encoder.
        
        @param item: MetaEncode
            The meta encode of the list items.
        @param identifier: object|None
            The identifier of the encoded collection.
           
        @ivar attributes: list[MetaEncode]
            The meta encode for the collection attributes.
        '''
        assert isinstance(item, MetaEncode), 'Invalid item encoder %s' % item

        self.identifier = identifier
        self.item = item
        self.attributes = []

    def encode(self, obj, context):
        '''
        MetaEncode.encode
        '''
        return Collection(identifier=self.identifier, value=obj, item=self.item, attributes=self.attributes)

class EncodeFirst(MetaEncode):
    '''
    Encoder that relays on a list of contained encoders when the encode event is received it will call the first encoder
    if it returns None it will go to the next encoder until one of the encoders will provide a value object.
    '''

    def __init__(self):
        '''
        Construct the first encode.
        
        @ivar encoders: list[MetaEncode]
            The encoders used.
        '''
        self.encoders = []

    def encode(self, obj, context):
        '''
        MetaEncode.encode
        '''
        for encode in self.encoders:
            assert isinstance(encode, MetaEncode), 'Invalid encode %s' % encode
            value = encode.encode(obj, context)
            if value is not None: return value

class EncodeMerge(MetaEncode):
    '''
    Encoder that uses the assigned encoders, if the returned values of the encoders have the same value then this encoder
    will return a Value object containing that value, otherwise it will return and object having the as properties
    encoders that will return the values. 
    '''

    class EncodeGet(MetaEncode):
        '''
        Used for getting the values from a dictionary whenever the merge fails.
        '''

        def __init__(self, key):
            '''
            Construct the merger get.
            
            @param key: object
                The key used in getting the value from the dictionary object.
            '''
            self.key = key

        def encode(self, obj, context):
            '''
            MetaEncode.encode
            '''
            assert isinstance(obj, dict), 'Invalid object %s' % obj
            return obj.get(self.key)

    def __init__(self, identifier=None):
        '''
        Construct the first encode.
        
        @param identifier: object|None
            The identifier to use on the merged return value.
        
        @ivar encoders: list[MetaEncode]
            The encoders used.
        '''
        self._encoders = []
        self._getters = []

    def assign(self, encoder):
        '''
        Assign a new encoder for merging.
        
        @param encoder: MetaEncode
            The meta encoder to be merged.
        '''
        assert isinstance(encoder, MetaEncode), 'Invalid encoder %s' % encoder
        self._getters.append(self.EncodeGet(len(self._encoders)))
        self._encoders.append(encoder)

    def encode(self, obj, context):
        '''
        MetaEncode.encode
        '''
        values, merge = {}, True
        for k, encode in enumerate(self._encoders):
            assert isinstance(encode, MetaEncode), 'Invalid encode %s' % encode
            value = encode.encode(obj, context)
            if value is None: merge = False
            else: values[k] = value
        # If all encoders have values and the merge process is ok we only need to check to see if all values are the same.
        if merge:
            value = reduce(lambda value, item: value if value == item else None, values.values())
            if value is not None: return Value(identifier=self.identifier, value=value)

        return Object(identifier=self.identifier, value=values, properties=self._getters)
