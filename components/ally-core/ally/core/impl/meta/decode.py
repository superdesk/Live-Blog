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
from ally.core.spec.meta import MetaDecode
from ally.core.spec.resources import Normalizer, Converter
from ally.exception import DevelError
from collections import deque

# --------------------------------------------------------------------

class DecodeRootString(MetaDecode):
    '''
    Provides an implementation for the @see: MetaDecode that behaves like a string root, meaning allows only string
    types (string, deque[string], list[string], tuple(string)), if the type is string then it transforms the identifier 
    to a deque[string] based on a separator.
    '''

    def __init__(self, separator, root):
        '''
        Construct the decode node.
        
        @param separator: string
            The separator to be used for converting the string identifier.
        @param root: MetaDecode
            The root meta decode, usually this meta decode and its children only accept deque[string].
        '''
        assert isinstance(separator, str), 'Invalid separator %s' % separator
        assert isinstance(root, MetaDecode), 'Invalid root %s' % root

        self.separator = separator
        self.root = root

    def decode(self, identifier, value, obj, context):
        '''
        @see: MetaDecode.decode
        '''
        if isinstance(identifier, str): identifier = identifier.split(self.separator)
        if isinstance(identifier, (list, tuple)): identifier = deque(identifier)

        if not isinstance(identifier, deque):
            raise DevelError('Invalid identifier %s, expected a string or string collection' % identifier)

        return self.root.decode(identifier, value, obj, context)

class DecodeNode(MetaDecode):
    '''
    Provides an implementation for the @see: MetaDecode that dispatches the decode event to the assigned decoder with
    the first path as a key.
    
    Only recognizes the identifier as being a deque[string].
    '''

    def __init__(self):
        '''
        Construct the decode node.
        
        @ivar decoders: dictionary{string, MetaDecode}
            A dictionary that will be used in finding the child decoder for the first path element.
        '''
        self.decoders = {}

    def decode(self, identifier, value, obj, context):
        '''
        @see: MetaDecode.decode
        '''
        assert isinstance(context, ContextParse), 'Invalid context %s' % context
        assert isinstance(context.normalizer, Normalizer)

        if not isinstance(identifier, deque): return False
        assert isinstance(identifier, deque)

        if identifier:
            path = identifier[0]
            for key, decoder in self.decoders.items():
                if path == context.normalizer.normalize(key):
                    assert isinstance(decoder, MetaDecode), 'Invalid meta decode %s' % decoder
                    identifier.popleft()
                    return decoder.decode(identifier, value, obj, context)
                    break
        return False

class DecodeSequence(MetaDecode):
    '''
    Provides an implementation for the @see: MetaDecode that dispatches the decode event to a list of decoders, will stop
    as soon as a decoder will return True.
    
    Only recognizes the identifier as being a deque[string].
    '''

    def __init__(self):
        '''
        Construct the decode node.
        
        @ivar decoders: list[MetaDecode]
            A list of meta decoders, the order is important since the decoding will stop at the first decoder that
            returns True.
        '''
        self.decoders = []

    def decode(self, identifier, value, obj, context):
        '''
        @see: MetaDecode.decode
        '''
        if not isinstance(identifier, deque): return False
        assert isinstance(identifier, deque)

        for decoder in self.decoders:
            assert isinstance(decoder, MetaDecode), 'Invalid meta decode %s' % decoder
            if decoder.decode(identifier, value, obj, context): return True
        return False

class DecodeSet(MetaDecode, WithSetter):
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
        MetaDecode.decode
        '''
        if not isinstance(identifier, deque): return False
        assert isinstance(identifier, deque)
        if identifier: return False
        # If there are more elements in the paths it means that this decoder should not process the value

        self.setter(obj, value)
        return True

class DecodeValue(MetaDecode, WithSetter):
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
        MetaDecode.decode
        '''
        assert isinstance(context, ContextParse), 'Invalid context %s' % context
        assert isinstance(context.converter, Converter)

        if not isinstance(identifier, deque): return False
        assert isinstance(identifier, deque)
        if identifier: return False
        # If there are more elements in the paths it means that this decoder should not process the value

        if not isinstance(value, str): return False
        # If the value is not a string then is not valid
        try: value = context.converter.asValue(value, self.type)
        except ValueError: raise DevelError('Expected type %s' % self.type)

        self.setter(obj, value)
        return True

class DecodeList(MetaDecode, WithSetter, WithGetter):
    '''
    Provides the list types decoding.
    
    Only recognizes the identifier as being a deque[string].
    '''

    def __init__(self, setter, getter, itemDecode):
        '''
        Construct the list decoder. The getter is used to pull the list from the repository object.
        @see: WithSetter.__init__
        @see: WithGetter.__init__
        
        @param itemDecode: MetaDecode
            The list item decoder.
        '''
        assert isinstance(itemDecode, MetaDecode), 'Invalid item decode %s' % itemDecode
        WithSetter.__init__(self, setter)
        WithGetter.__init__(self, getter)

        self.itemDecode = itemDecode

    def decode(self, identifier, value, obj, context):
        '''
        MetaDecode.decode
        '''
        if not isinstance(identifier, deque): return False
        assert isinstance(identifier, deque)

        if isinstance(value, (list, tuple)): values = value
        else: values = [value]

        items = []
        for value in values:
            if not self.itemDecode.decode(identifier, value, items, context): return False

        objList = self.getter(obj)
        if objList is None:
            self.setter(obj, items)
        else:
            assert isinstance(objList, list), 'Invalid list %s provided by getter' % objList
            objList.extend(items)

        return True
