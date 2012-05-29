'''
Created on May 23, 2012

@package: ally core
@copyright: 2012 Sourcefabric o.p.s.
@license: http://www.gnu.org/licenses/gpl-3.0.txt
@author: Gabriel Nistor

Provides basic meta encode implementations, the encoders only work with string type identifiers
like: None, string, tuple(string). 
'''

from ally.api.type import Type
from ally.core.impl.meta.general import WithGetter, ContextParse, WithIdentifier
from ally.core.spec.meta import IMetaEncode, Value, Collection, Object, Meta, \
    SAMPLE
from ally.core.spec.resources import Converter, Normalizer
from collections import deque, Iterable
from itertools import chain

# --------------------------------------------------------------------

class EncodeIdentifier(IMetaEncode, WithIdentifier):
    '''
    Encoder that just sets an identifier on the returned meta from a contained encoder.
    
    Only accepts string identifiers like: string|list[string]|tuple(string)
    '''

    def __init__(self, encoder, identifier):
        '''
        Construct with identifier.
        @see: WithIdentifier.__init__
        
        @param encoder: IMetaEncode
            The meta encode to set the identifier to the returned meta.
        '''
        assert isinstance(encoder, IMetaEncode), 'Invalid encoder %s' % encoder
        WithIdentifier.__init__(self, identifier)

        self.encoder = encoder

    def encode(self, obj, context):
        '''
        IMetaEncode.encode
        '''
        assert isinstance(context, ContextParse), 'Invalid context %s' % context
        assert isinstance(context.normalizer, Normalizer)

        meta = self.encoder.encode(obj, context)
        if meta is not None:
            assert isinstance(meta, Meta), 'Invalid meta return value %s' % meta
            if isinstance(self.identifier, str): meta.identifier = self.identifier
            else: meta.identifier = tuple(context.normalizer.normalize(iden) for iden in self.identifier)
            return meta

class EncodeGetter(IMetaEncode, WithGetter):
    '''
    An encode that actually just uses a getter to fetch a value from the object and pass it to the contained encoder.
    If the value fetched is None than this encode will return None and not delegate to the contained encoder.
    '''

    def __init__(self, encoder, getter):
        '''
        Construct the get encoder.
        @see: WithGetter.__init__
        
        @param encoder: IMetaEncode
            The meta encode to delegate with the obtained value.
        '''
        assert isinstance(encoder, IMetaEncode), 'Invalid encoder %s' % encoder
        WithGetter.__init__(self, getter)

        self.encoder = encoder

    def encode(self, obj, context):
        '''
        IMetaEncode.encode
        '''
        if obj is not None:
            if obj is SAMPLE: value = SAMPLE
            else: value = self.getter(obj)
            if value is not None: return self.encoder.encode(value, context)

class EncodeGetterIdentifier(EncodeGetter, WithIdentifier):
    '''
    Encode that provides also the functionality of @see: EncodeGetter and @see: EncodeIdentifier
    '''

    def __init__(self, encoder, getter, identifier):
        '''
        Construct the get encoder.
        @see: EncodeGetter.__init__
        @see: WithIdentifier.__init__
        '''
        EncodeGetter.__init__(self, encoder, getter)
        WithIdentifier.__init__(self, identifier)

    def encode(self, obj, context):
        '''
        IMetaEncode.encode
        '''
        assert isinstance(context, ContextParse), 'Invalid context %s' % context
        assert isinstance(context.normalizer, Normalizer)

        meta = EncodeGetter.encode(self, obj, context)
        if meta is not None:
            assert isinstance(meta, Meta), 'Invalid meta return value %s' % meta
            if isinstance(self.identifier, str): meta.identifier = self.identifier
            else: meta.identifier = tuple(context.normalizer.normalize(iden) for iden in self.identifier)
            return meta

class EncodeGetValue(IMetaEncode, WithGetter):
    '''
    An encode that actually just uses a getter to fetch a value from the object and return it wrapped in a Value meta.
    '''

    def __init__(self, getter):
        '''
        Construct the get value.
        @see: WithGetter.__init__
        '''
        WithGetter.__init__(self, getter)

    def encode(self, obj, context):
        '''
        IMetaEncode.encode
        '''
        if obj is not None:
            if obj is SAMPLE: value = SAMPLE
            else: value = self.getter(obj)
            if value is not None: return Value(value=value)

class EncodeValue(IMetaEncode):
    '''
    Encodes the object to a string value by using the converter.
    '''

    def __init__(self, type):
        '''
        Construct the type based encoder.
        
        @param type: Type
            The type represented by the encoder.
        '''
        assert isinstance(type, Type), 'Invalid type %s' % type

        self.type = type

    def encode(self, obj, context):
        '''
        IMetaEncode.encode
        '''
        assert isinstance(context, ContextParse), 'Invalid context %s' % context
        assert isinstance(context.converter, Converter)

        if obj is SAMPLE: value = 'a %s value' % self.type
        else: value = context.converter.asString(obj, self.type)
        return Value(value=value)

class EncodeObject(IMetaEncode):
    '''
    Provides support for encoding an object.
    '''

    def __init__(self):
        '''
        Construct the object encoder.
        
        @ivar properties: list[IMetaEncode]
            The meta encode for the object properties.
        '''
        self.properties = []

    def encode(self, obj, context):
        '''
        IMetaEncode.encode
        '''
        properties = (encode.encode(obj, context) for encode in self.properties)
        return Object(properties=properties)

class EncodeObjectExploded(EncodeObject):
    '''
    Encoder that explodes the returned Object properties.
    
    Only handles string type identifiers like: string, list[string], tuple(string)
    '''

    def __init__(self):
        '''
        Construct the encode exploded.
        @see: EncodeObject.__init__
        '''
        super().__init__()

    def encode(self, obj, context):
        '''
        IMetaEncode.encode
        '''
        metas = deque()
        for encode in self.properties:
            assert isinstance(encode, IMetaEncode), 'Invalid encode %s' % encode
            meta = encode.encode(obj, context)
            if meta is not None: self.process(self.push([], meta), meta, metas)

        if metas: return Object(properties=iter(metas))

    def process(self, identifier, meta, metas):
        '''
        Processes the exploding for the provided meta.
        
        @param identifier: list[string]
            The identifier to be associated with the current meta.
        @param meta: Meta
            The meta to process the explode for.
        @param metas: deque[Meta]
            The list of exploded Meta.
        '''
        assert isinstance(metas, deque), 'Invalid metas %s' % identifier
        if isinstance(meta, Object):
            assert isinstance(meta, Object)
            for prop in meta.properties:
                if prop is None: continue
                assert isinstance(prop, Meta), 'Invalid encode meta return %s' % prop
                self.process(self.push(identifier, prop), prop, metas)

        else:
            assert isinstance(meta, Meta), 'Invalid meta %s' % meta
            meta.identifier = identifier
            metas.append(meta)

    def push(self, identifier, meta):
        '''
        Pushes into the provided identifier list the identifier of the provided meta.
        
        @param identifier: list[string]
            The identifier.
        @param meta: Meta
            The meta to have the identifier pushed.
        @return: list[string]
            The adjusted identifier.
        '''
        assert isinstance(meta, Meta), 'Invalid meta %s' % meta
        assert isinstance(identifier, list), 'Invalid identifier %s' % identifier

        if meta.identifier is not None:
            identifier = list(identifier)
            if isinstance(meta.identifier, str): identifier.append(meta.identifier)
            else:
                assert isinstance(meta.identifier, (tuple, list)), 'Invalid identifier %s' % meta.identifier
                if __debug__:
                    for iden in meta.identifier:
                        assert isinstance(iden, str), 'Invalid identifier element %s in %s' % (iden, str(meta.identifier))
                identifier.extend(meta.identifier)

        return identifier

class EncodeCollection(IMetaEncode):
    '''
    Provides support for encoding a collection.
    '''

    def __init__(self, itemEncode):
        '''
        Construct the collection encoder.
        
        @param itemEncode: IMetaEncode
            The meta encode of the list items.
        '''
        assert isinstance(itemEncode, IMetaEncode), 'Invalid item encoder %s' % itemEncode

        self.itemEncode = itemEncode

    def encode(self, obj, context):
        '''
        IMetaEncode.encode
        '''
        assert isinstance(obj, Iterable), 'Invalid object %s' % obj
        items = (self.itemEncode.encode(item, context) for item in obj)
        return Collection(items=items)

class EncodeMerge(IMetaEncode):
    '''
    Encoder that uses the assigned encoders, if the returned values of the encoders have the same value then this encoder
    will return a Value meta containing that value, otherwise it will return an Object meta having as the properties the
    returned meta of the encoders. 
    '''

    def __init__(self):
        '''
        Construct the first encode.
        
        @ivar encoders: list[IMetaEncode]
            The encoders used.
        '''
        self.encoders = []

    def encode(self, obj, context):
        '''
        IMetaEncode.encode
        '''
        metas, merge = deque(), True
        for encode in self.encoders:
            assert isinstance(encode, IMetaEncode), 'Invalid encode %s' % encode
            meta = encode.encode(obj, context)

            if meta is None: merge = False
            else:
                merge = merge and isinstance(meta, Value)
                metas.append(meta)

        # If all encoders have values and the merge process is ok we only need to check to see if all values are the same.
        if merge:
            values = iter(metas)
            value = next(values)
            assert isinstance(value, Value)
            for item in values:
                assert isinstance(item, Value)
                merge = merge and value.value == item.value

            if merge: return Value(value=value.value)

        return Object(properties=iter(metas))

class EncodeJoin(IMetaEncode):
    '''
    Provides a @see: IMetaEncode that joins the returned meta Collection if the collection items are all meta Value of
    string. So if the assigned encoder returns a Collection meta of Value string it will join that.
    '''

    def __init__(self, encoder, separator, separatorEscape=None):
        '''
        Construct the list with separator.
        @see: DecodeList.__init__
        
        @param encoder: IMetaEncode
            The encoder to join the Collection for.
        @param separator: string
            The separator to use to join the values.
        @param separatorEscape: string|None
            The value to use in escaping the separator string in the value items.
        '''
        assert isinstance(encoder, IMetaEncode), 'Invalid encoder %s' % encoder
        assert isinstance(separator, str), 'Invalid separator %s' % separator
        assert separatorEscape is None or isinstance(separatorEscape, str), \
        'Invalid separator escape %s' % separatorEscape

        self.encoder = encoder
        self.separator = separator
        self.separatorEscape = separatorEscape

    def encode(self, obj, context):
        '''
        IMetaEncode.encode
        '''
        meta = self.encoder.encode(obj, context)
        if meta is not None: return self.process(meta)

    def tryJoin(self, identifier, metas):
        '''
        Try to join the provided meta's. If the join fails this method will return all the values that have been polled
        from the meta's Iterator.
        
        @param identifier: object|None
            The identifier to use on the joined value.
        @param metas: Iterable[Meta]
            The meta to process.
        @return: list[Value]|Value
            In case the join failed it will return a list of Value objects that have been pooled from the metas, otherwise
            it will return a Value.
        '''
        assert isinstance(metas, Iterable), 'Invalid metas %s' % metas

        values = deque()
        for meta in metas:
            if meta is None: continue
            if isinstance(meta, Value):
                values.append(meta)

                assert isinstance(meta, Value)
                if not isinstance(meta.value, str):
                    # The item value is not string so will return it as it is.
                    return values
            else:
                return values

        if self.separatorEscape is not None:
            values = [value.value.replace(self.separator, self.separatorEscape) for value in values]
        else:
            values = [value.value for value in values]

        return Value(identifier, self.separator.join(values))

    def process(self, meta):
        '''
        Process the meta for joining.
        
        @param meta: Meta
            The meta to process.
        '''
        assert isinstance(meta, Meta), 'Invalid meta %s' % meta

        if isinstance(meta, Collection):
            assert isinstance(meta, Collection)
            items = iter(meta.items)
            tried = self.tryJoin(meta.identifier, items)
            if isinstance(tried, Value): return tried

            meta.items = chain(tried, self.wrap(items))
        elif isinstance(meta, Object):
            assert isinstance(meta, Object)
            # We will check if any of the child meta will be valid for join
            meta.properties = self.wrap(meta.properties)

        return meta

    def wrap(self, metas):
        '''
        Wraps the metas for joining.
        
        @param metas: Iterable[Meta]
            The meta to wrap.
        '''
        assert isinstance(metas, Iterable), 'Invalid metas %s' % metas

        for meta in metas:
            if meta is None: continue

            yield self.process(meta)
