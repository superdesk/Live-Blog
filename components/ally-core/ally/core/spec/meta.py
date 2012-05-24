'''
Created on May 21, 2012

@package: ally core
@copyright: 2012 Sourcefabric o.p.s.
@license: http://www.gnu.org/licenses/gpl-3.0.txt
@author: Gabriel Nistor

Provides the meta specifications. 
'''

from ally.support.util import MetaClassBean
import abc

# --------------------------------------------------------------------

MetaClassBean = MetaClassBean # Just to avoid IDE warning
class Context(metaclass=MetaClassBean):
    '''
    A simple class that is a container for the context data.
    '''

    def __init__(self, **keyargs):
        '''
        Construct a context with the provided key arguments as context data.
        '''
        for key, value in keyargs.items(): setattr(self, key, value)

class Value(metaclass=MetaClassBean):
    '''
    The value returned by the encode.
    
    @ivar identifier: object
        The identifier associated with the encoded value.
    @ivar  value: object
        The value encoded.
    ...
        Beside this values in this class there might be others depending on the nature of the meta encode, is
        the duty of the meta encoder users to check and use the extra information found in a value.
    '''
    identifier = object
    value = object

    def __init__(self, **keyargs):
        '''
        Construct a value with the provided key arguments as data.
        '''
        for key, value in keyargs.items(): setattr(self, key, value)

# --------------------------------------------------------------------

class MetaDecode(metaclass=abc.ABCMeta):
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

class MetaEncode(metaclass=abc.ABCMeta):
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
        @return: Value|None
            Returns the encoded value, None if their is nothing to encode for the provided object.
        '''

class IMetaService(metaclass=abc.ABCMeta):
    '''
    Service specification that provides that handles meta.
    '''

    @abc.abstractclassmethod
    def createDecode(self, invoker):
        '''
        Create the meta decode specific for this service based on the provided invoker.
        
        @param invoker: Invoker
            The invoker to create the meta decode for.
        @return: MetaDecode
            The created meta decode.
        '''

    @abc.abstractclassmethod
    def createEncode(self, invoker):
        '''
        Create the meta encoder specific for this service based on the provided invoker.
        
        @param invoker: Invoker
            The invoker to create the meta encode for.
        @return: MetaEncode
            The created meta encode.
        '''

# --------------------------------------------------------------------

class Object(Value):
    '''
    Provides an object value.
    
    @ivar properties: list[MetaEncode]
        The properties encoders for the object.
    @ivar attributes: list[MetaEncode]
        The attributes encoders for the object.
    '''
    properties = list
    attributes = list

class Collection(Value):
    '''
    Provides a collection value.
    
    @ivar item: MetaEncode
        The meta encode to use on the value items.
    @ivar attributes: list[MetaEncode]
        The attributes encoders for the object.
    '''
    item = MetaEncode
    attributes = list
