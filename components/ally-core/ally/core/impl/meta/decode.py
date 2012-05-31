'''
Created on May 23, 2012

@package: ally core
@copyright: 2012 Sourcefabric o.p.s.
@license: http://www.gnu.org/licenses/gpl-3.0.txt
@author: Gabriel Nistor

Provides basic meta decode implementations. 
'''

from .general import ContextParse, WithSetter, WithGetter
from ally.api.type import Type
from ally.core.impl.meta.general import WithIdentifier
from ally.core.spec.meta import IMetaDecode
from ally.core.spec.resources import Normalizer, Converter
from collections import deque

# --------------------------------------------------------------------

class DecodeIdentifier(IMetaDecode, WithIdentifier):
    '''
    Decoder that just checks if a identifier is in path, if so delegate to the contained decoder.
    
    Only recognizes the identifier as being a deque[string].
    '''

    def __init__(self, decoder, identifier):
        '''
        Construct with identifier.
        @see: WithIdentifier.__init__
        
        @param decoder: IMetaDecode
            The meta decode to delegate to if identifier is checked.
        '''
        assert isinstance(decoder, IMetaDecode), 'Invalid decoder %s' % decoder
        WithIdentifier.__init__(self, identifier)

        self.decoder = decoder

    def decode(self, identifier, value, obj, context):
        '''
        @see: IMetaDecode.decode
        '''
        assert isinstance(context, ContextParse), 'Invalid context %s' % context
        assert isinstance(context.normalizer, Normalizer), 'Invalid normalizer %s' % context.normalizer

        if not isinstance(identifier, deque): return False
        assert isinstance(identifier, deque)
        if not identifier: return False

        if isinstance(self.identifier, str):
            if context.normalizer.normalize(self.identifier) != identifier[0]: return False
            identifier.popleft()
        else:
            if len(identifier) < len(self.identifier): return False
            for iden1, iden2 in zip(self.identifier, identifier):
                if context.normalizer.normalize(iden1) != iden2: return False
            for _k in range(0, len(self.identifier)): identifier.popleft()

        return self.decoder.decode(identifier, value, obj, context)

class DecodeGetter(IMetaDecode, WithGetter):
    '''
    An encode that actually just uses a getter to fetch a value from the object and pass it to the contained decoder.
    If the value fetched is None than this decode will return False and not delegate to the contained decoder.
    '''

    def __init__(self, decoder, getter):
        '''
        Construct the get decoder.
        @see: WithGetter.__init__
        
        @param decoder: IMetaDecode
            The decoder to delegate with the obtained value.
        '''
        assert isinstance(decoder, IMetaDecode), 'Invalid decoder %s' % decoder
        WithGetter.__init__(self, getter)

        self.decoder = decoder

    def decode(self, identifier, value, obj, context):
        '''
        IMetaDecode.decode
        '''
        obj = self.getter(obj)
        if obj is None: return False
        return self.decoder.decode(identifier, value, obj, context)

class DecodeGetterIdentifier(DecodeIdentifier):
    '''
    Decode that provides also the functionality of @see: DecodeGetter and @see: DecodeIdentifier
    '''

    def __init__(self, decoder, getter, identifier):
        '''
        Construct the get decoder.
        @see: DecodeIdentifier.__init__
        @see: DecodeGetter.__init__
        '''
        DecodeIdentifier.__init__(self, DecodeGetter(decoder, getter), identifier)

class DecodeSetValue(IMetaDecode, WithSetter):
    '''
    Sets the received value directly.
    
    Only recognizes the identifier as being a deque[string].
    '''

    def __init__(self, setter):
        '''
        Construct the set decoder.
        @see: WithSetter.__init__
        '''
        WithSetter.__init__(self, setter)

    def decode(self, identifier, value, obj, context):
        '''
        IMetaDecode.decode
        '''
        if not isinstance(identifier, deque): return False
        if identifier: return False
        # If there are more elements in the paths it means that this decoder should not process the value

        self.setter(obj, value)
        return True

class DecodeValue(IMetaDecode, WithSetter):
    '''
    Processes the string value to an object based on the assigned type by using the converter.
    
    Only recognizes the identifier as being a deque[string].
    '''

    def __init__(self, setter, type):
        '''
        Construct the type based decoder.
        @see: WithSetter.__init__
        
        @param type: Type
            The type represented by the decoder.
        '''
        assert isinstance(type, Type), 'Invalid type %s' % type
        WithSetter.__init__(self, setter)

        self.type = type

    def decode(self, identifier, value, obj, context):
        '''
        IMetaDecode.decode
        '''
        assert isinstance(context, ContextParse), 'Invalid context %s' % context
        assert isinstance(context.converter, Converter)

        if not isinstance(identifier, deque): return False
        if identifier: return False
        # If there are more elements in the paths it means that this decoder should not process the value

        if not isinstance(value, str): return False
        # If the value is not a string then is not valid
        try: value = context.converter.asValue(value, self.type)
        except ValueError: return False

        self.setter(obj, value)
        return True

class DecodeObject(IMetaDecode):
    '''
    Provides an implementation for the @see: IMetaDecode that dispatches the decode event to the assigned decoder with
    the first path as a key.
    
    Only recognizes the identifier as being a deque[string].
    '''

    def __init__(self):
        '''
        Construct the decode node.
        
        @ivar properties: dictionary{string, IMetaDecode}
            A dictionary that will be used in finding the child decoder for the first path element.
        '''
        self.properties = {}

    def decode(self, identifier, value, obj, context):
        '''
        @see: IMetaDecode.decode
        '''
        assert isinstance(context, ContextParse), 'Invalid context %s' % context
        assert isinstance(context.normalizer, Normalizer), 'Invalid normalizer %s' % context.normalizer

        if not isinstance(identifier, deque): return False
        assert isinstance(identifier, deque)
        if not identifier: return False

        path = identifier[0]
        for key, decoder in self.properties.items():
            if path == context.normalizer.normalize(key):
                assert isinstance(decoder, IMetaDecode), 'Invalid meta decode %s' % decoder
                identifier.popleft()
                return decoder.decode(identifier, value, obj, context)
        return False

class DecodeList(IMetaDecode):
    '''
    Provides the list types decoding.
    
    Only recognizes the identifier as being a deque[string].
    '''

    def __init__(self, itemDecode):
        '''
        Construct the list decoder.
        
        @param itemDecode: IMetaDecode
            The list item decoder.
        '''
        assert isinstance(itemDecode, IMetaDecode), 'Invalid item decode %s' % itemDecode

        self.itemDecode = itemDecode

    def decode(self, identifier, value, obj, context):
        '''
        IMetaDecode.decode
        '''
        if not isinstance(obj, list): return False
        if not isinstance(identifier, deque): return False

        if isinstance(value, (list, tuple)): values = value
        else: values = [value]

        for value in values:
            if not self.itemDecode.decode(identifier, value, obj, context): return False

        return True

class DecodeFirst(IMetaDecode):
    '''
    Provides an implementation for the @see: IMetaDecode that dispatches the decode event to a list of decoders, will stop
    as soon as a decoder will return True.
    
    Only recognizes the identifier as being a deque[string].
    '''

    def __init__(self):
        '''
        Construct the decode node.
        
        @ivar decoders: list[IMetaDecode]
            A list of meta decoders, the order is important since the decoding will stop at the first decoder that
            returns True.
        '''
        self.decoders = []

    def decode(self, identifier, value, obj, context):
        '''
        @see: IMetaDecode.decode
        '''
        if not isinstance(identifier, deque): return False

        for decoder in self.decoders:
            assert isinstance(decoder, IMetaDecode), 'Invalid meta decode %s' % decoder
            if decoder.decode(identifier, value, obj, context): return True
        return False


class DecodeSplit(IMetaDecode):
    '''
    Provides a @see: IMetaDecode that splits a string value into a list of values, if the received value is not a string
    then it will be delegated to the contained decoder as it is. 
    '''

    def __init__(self, decoder, splitValues, normalizeValue=None):
        '''
        Construct the list with separator.
        @see: DecodeList.__init__
        
        @param decoder: IMetaDecode
            The decoder to delegate to.
        @param splitValues: complied regex
            The regex to use in spliting the values.
        @param normalizeValue: complied regex|None
            The regex to use in normalizing the splited values, if None no normalization will occur.
        '''
        assert isinstance(decoder, IMetaDecode), 'Invalid decoder %s' % decoder
        assert splitValues is not None, 'A split values regex is required'

        self.decoder = decoder
        self.splitValues = splitValues
        self.normalizeValue = normalizeValue

    def decode(self, identifier, value, obj, context):
        '''
        @see: IMetaDecode.decode
        '''
        if isinstance(value, str):
            value = self.splitValues.split(value)
            if self.normalizeValue is not None:
                for k in range(0, len(value)): value[k] = self.normalizeValue.sub('', value[k])

        return self.decoder.decode(identifier, value, obj, context)
