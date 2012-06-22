'''
Created on May 21, 2012

@package: ally core
@copyright: 2012 Sourcefabric o.p.s.
@license: http://www.gnu.org/licenses/gpl-3.0.txt
@author: Gabriel Nistor

Provides the meta specifications. 
'''

from collections import Iterable
import abc

# --------------------------------------------------------------------

SAMPLE = object() # Marker used to instruct the encoders to provide a sample.

class Meta:
    '''
    The referenced encoded meta.

    Beside this values in this class there might be others depending on the nature of the meta encode, is
    the duty of the meta encoder users to check and use the extra information found in a meta.
    '''
    __slots__ = ('identifier',)

    def __init__(self, identifier=None):
        '''
        Construct a meta.
        
        @param identifier: object|None
            The identifier associated with the encoded meta.
        '''
        self.identifier = identifier

class Value(Meta):
    '''
    Provides a value meta.
    '''
    __slots__ = ('value',)

    def __init__(self, identifier=None, value=None):
        '''
        Construct a value.
        @see: Meta.__init__
        
        @param value: object|None
            The value associated with the value meta.
        '''
        Meta.__init__(self, identifier)

        self.value = value

class Attributed(Meta):
    '''
    Provides an attributed meta.
    '''
    __slots__ = ('attributes',)

    def __init__(self, identifier=None, attributes=()):
        '''
        Construct an attributed meta.
        @see: Meta.__init__
        
        @param attributes: Iterable
            The attributes associated with the attributed meta.
        '''
        assert isinstance(attributes, Iterable), 'Invalid attributes %s' % attributes
        Meta.__init__(self, identifier)

        self.attributes = attributes

class Object(Meta):
    '''
    Provides an object meta.
    '''
    __slots__ = ('properties',)

    def __init__(self, identifier=None, properties=()):
        '''
        Construct an object meta.
        @see: Meta.__init__
        
        @param properties: Iterable
            The properties associated with the object meta.
        '''
        assert isinstance(properties, Iterable), 'Invalid properties %s' % properties
        Meta.__init__(self, identifier)

        self.properties = properties

class Collection(Meta):
    '''
    Provides a collection meta.
    '''
    __slots__ = ('items',)

    def __init__(self, identifier=None, items=()):
        '''
        Construct a collection meta.
        @see: Meta.__init__
        
        @param items: Iterable
            The items associated with the collection meta.
        '''
        assert isinstance(items, Iterable), 'Invalid items %s' % items
        Meta.__init__(self, identifier)

        self.items = items

# --------------------------------------------------------------------

class IMetaDecode(metaclass=abc.ABCMeta):
    '''
    Provides the specification class for a meta that decodes data. 
    '''

    @abc.abstractclassmethod
    def decode(self, identifier, value, obj, context):
        '''
        Decode the value that is specific for the provided identifier. The object represents the data repository where 
        to place the decoded value.
        
        @param identifier: object
            The identifier used to associated the value with the object.
        @param value: object
            The value to get decoded.
        @param obj: object
            The data repository object.
        @param context: Context
            The data context used in the decoding, this will contain all the support required by the decoding.
        @return: boolean
            True if the decode was successful, False otherwise.
        '''

class IMetaEncode(metaclass=abc.ABCMeta):
    '''
    Provides the specification class for a meta that encodes data. 
    '''

    @abc.abstractclassmethod
    def encode(self, obj, context):
        '''
        Encode the object to an identifier and a value.

        @param obj: object
            The object to be encoded.
        @param context: Context
            The data context used in the decoding, this will contain all the support required by the decoding.
        @return: Meta|None
            Returns the encoded meta, None if their is nothing to encode for the provided object.
        '''
