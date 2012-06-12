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
from ally.core.impl.meta.general import WithGetter, WithIdentifier
from ally.core.spec.meta import IMetaEncode, Value, Collection, Object, Meta, \
    SAMPLE
from ally.core.spec.resources import Converter, Normalizer
from collections import deque, Iterable
from itertools import chain
from ally.core.spec.extension import CharConvert

# --------------------------------------------------------------------

class WithEncoder:
    '''
    Provides a base class that requires an encoder.
    '''

    def __init__(self, encoder):
        '''
        Construct the encode wrapper.
        
        @param encoder: IMetaEncode
            The encoder to be wrapped.
        '''
        assert isinstance(encoder, IMetaEncode), 'Invalid encoder %s' % encoder

        self.encoder = encoder

# --------------------------------------------------------------------

class EncodeIdentifier(IMetaEncode, WithEncoder, WithIdentifier):
    '''
    Encoder that just sets an identifier on the returned meta from a contained encoder.
    
    Only accepts string identifiers like: string|list[string]|tuple(string)
    '''

    def __init__(self, encoder, identifier):
        '''
        Construct with identifier.
        @see: WithEncoder.__init__
        @see: WithIdentifier.__init__
        
        @param encoder: IMetaEncode
            The meta encode to set the identifier to the returned meta.
        '''
        WithEncoder.__init__(self, encoder)
        WithIdentifier.__init__(self, identifier)

    def encode(self, obj, context):
        '''
        IMetaEncode.encode
        '''
        assert isinstance(context, CharConvert), 'Invalid context %s' % context
        assert isinstance(context.normalizer, Normalizer)

        meta = self.encoder.encode(obj, context)
        if meta is not None:
            assert isinstance(meta, Meta), 'Invalid meta return value %s' % meta
            if isinstance(self.identifier, str): meta.identifier = context.normalizer.normalize(self.identifier)
            else: meta.identifier = tuple(context.normalizer.normalize(iden) for iden in self.identifier)
            return meta

class EncodeGetter(IMetaEncode, WithEncoder, WithGetter):
    '''
    An encode that actually just uses a getter to fetch a value from the object and pass it to the contained encoder.
    If the value fetched is None than this encode will return None and not delegate to the contained encoder.
    '''

    def __init__(self, encoder, getter):
        '''
        Construct the get encoder.
        @see: WithEncoder.__init__
        @see: WithGetter.__init__
        
        @param encoder: IMetaEncode
            The meta encode to delegate with the obtained value.
        '''
        WithEncoder.__init__(self, encoder)
        WithGetter.__init__(self, getter)

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
        assert isinstance(context, CharConvert), 'Invalid context %s' % context
        assert isinstance(context.normalizer, Normalizer)

        meta = EncodeGetter.encode(self, obj, context)
        if meta is not None:
            assert isinstance(meta, Meta), 'Invalid meta return value %s' % meta
            if isinstance(self.identifier, str): meta.identifier = context.normalizer.normalize(self.identifier)
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
        assert isinstance(context, CharConvert), 'Invalid context %s' % context
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

class EncodeExploded(IMetaEncode, WithEncoder):
    '''
    Encoder that explodes the returned Object properties.
    
    Only handles string type identifiers like: string, list[string], tuple(string)
    '''

    def __init__(self, encoder):
        '''
        Construct the encode exploded.
        @see: WithEncoder.__init__
        
        @param encoder: IMetaEncode
            The encoder to explode.
        '''
        WithEncoder.__init__(self, encoder)

    def encode(self, obj, context):
        '''
        IMetaEncode.encode
        '''
        metas = deque()
        meta = self.encoder.encode(obj, context)
        if meta is not None: self.process(self.push([], meta), meta, metas)

        if metas: return Collection(items=iter(metas))

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

        elif isinstance(meta, Collection):
            assert isinstance(meta, Collection)
            for item in meta.items:
                if item is None: continue
                assert isinstance(item, Meta), 'Invalid encode meta return %s' % item
                self.process(self.push(identifier, item), item, metas)

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
        if obj is SAMPLE: obj = (SAMPLE,)
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

class EncodeJoin(IMetaEncode, WithEncoder):
    '''
    Provides a @see: IMetaEncode that joins the returned meta Collection if the collection items are all meta Value of
    string and have the same identifiers. So if the assigned encoder returns a Collection meta of Value string
    it will join that.
    '''

    def __init__(self, encoder, separator, separatorEscape=None):
        '''
        Construct the list with separator.
        @see: WithEncoder.__init__
        
        @param encoder: IMetaEncode
            The encoder to join the Collection for.
        @param separator: string
            The separator to use to join the values.
        @param separatorEscape: string|None
            The value to use in escaping the separator string in the value items.
        '''
        assert isinstance(separator, str), 'Invalid separator %s' % separator
        assert separatorEscape is None or isinstance(separatorEscape, str), \
        'Invalid separator escape %s' % separatorEscape
        WithEncoder.__init__(self, encoder)

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

        tried = deque()
        for meta in metas:
            if meta is None: continue
            tried.append(meta)
            if isinstance(meta, Value):
                assert isinstance(meta, Value)
                if not isinstance(meta.value, str) or tried[0].identifier != meta.identifier:
                    # The item value is not string or has a different identifier, so will return it as it is.
                    return tried
            else:
                return tried

        if not tried: return None

        if len(tried) > 1:
            if self.separatorEscape is not None:
                values = [value.value.replace(self.separator, self.separatorEscape) for value in tried]
            else:
                values = [value.value for value in tried]

            if not identifier: identifier = tried[0].identifier

            return Value(identifier, self.separator.join(values))
        return tried[0]

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

            meta.items = self.wrap(chain(tried, items))
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

class EncodeJoinIndentifier(EncodeExploded):
    '''
    Provides the parameters encode. It will explode the contained meta's and join the identifiers based on the
    separator.  
    '''

    def __init__(self, encoder, separator):
        '''
        Construct the encoder.
        @see: EncodeExploded.__init__
        
        @param separator: string
            The separator to be used for joining the string identifier.
        '''
        assert isinstance(separator, str), 'Invalid separator %s' % separator
        EncodeExploded.__init__(self, encoder)

        self.separator = separator

    def encode(self, obj, context):
        '''
        IMetaEncode.encode
        '''
        meta = super().encode(obj, context)
        if meta is not None:
            assert isinstance(meta, Collection), 'Invalid meta object %s' % meta
            meta.items = self.joinIdentifiers(meta.items)
            return meta

    def joinIdentifiers(self, metas):
        '''
        Join the identifiers from the provided metas.
        
        @param metas: Iterable[Meta]
            The meta's to join the identifiers for.
        '''
        assert isinstance(metas, Iterable), 'Invalid meta\'s' % metas
        for meta in metas:
            assert isinstance(meta, Value), 'Invalid meta %s, only Value expected' % meta
            if isinstance(meta.identifier, (list, tuple)):
                meta.identifier = self.separator.join(meta.identifier)
            yield meta
