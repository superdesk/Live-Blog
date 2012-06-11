'''
Created on Jun 1, 2012

@package: ally core
@copyright: 2012 Sourcefabric o.p.s.
@license: http://www.gnu.org/licenses/gpl-3.0.txt
@author: Gabriel Nistor

Contains the extension classes for the server request/response.
'''

from ally.core.spec.meta import Meta
from ally.core.spec.resources import Normalizer, Converter, Invoker
from ally.support.util_sys import validateTypeFor

# --------------------------------------------------------------------
# Extensions used for text based encoding/decoding

class CharSet:
    '''
    Container for text content specifications.
    
    @ivar charSet: string
        The character set for the content.
    '''
    __slots__ = ('charSet',)

    def __init__(self):
        '''
        Construct the content specifications.
        '''
        self.charSet = None

if __debug__:
    # Used to validate the values for the container in debug mode.
    validateTypeFor(CharSet, 'charSet', str)

class CharSetsAccepted:
    '''
    Container for accepted text content specifications.
    
    @ivar accCharSets: list[string]
        The character sets accepted for response.
    '''
    __slots__ = ('accCharSets',)

    def __init__(self):
        '''
        Construct the accepted text content specification.
        '''
        self.accCharSets = []

if __debug__:
    # Used to validate the values for the container in debug mode.
    validateTypeFor(CharSetsAccepted, 'accCharSets', list, False)

class CharConvert:
    '''
    The container with string transformation services.

    @ivar normalizer: Normalizer
        The normalizer to use.
    @ivar converter: Converter
        The converter to use.
    '''
    __slots__ = ('normalizer', 'converter')

    def __init__(self):
        '''
        Construct the conversion container.
        '''
        self.normalizer = None
        self.converter = None

if __debug__:
    # Used to validate the values for the container in debug mode.
    validateTypeFor(CharConvert, 'normalizer', Normalizer)
    validateTypeFor(CharConvert, 'converter', Converter)

class CharConvertModel(CharConvert):
    '''
    The container with string transformation services that has an aditional id converter.
    
    @ivar converterId: Converter
        The converter to use for model id's.
    '''
    __slots__ = ('converterId',)

    def __init__(self):
        '''
        Construct the conversion container.
        '''
        self.converterId = None

if __debug__:
    # Used to validate the values for the container in debug mode.
    validateTypeFor(CharConvertModel, 'converterId', Converter)

# --------------------------------------------------------------------
# General extensions

class TypeAccepted:
    '''
    Container for accepted content types.
    
    @ivar accTypes: list
        The content types accepted for response.
    '''
    __slots__ = ('accTypes',)

    def __init__(self):
        '''
        Construct the accepted content types.
        '''
        self.accTypes = []


if __debug__:
    # Used to validate the values for the container in debug mode.
    validateTypeFor(TypeAccepted, 'accTypes', list, False)

class Invoke:
    '''
    Container for invoking.
    
    @ivar invoker: Invoker
        The invoker to be used for calling the service.
    @ivar arguments: dictionary{string, object}
        A dictionary containing as a key the argument name, this dictionary needs to be populated by the 
        processors as seen fit, also the parameters need to be transformed to arguments.
    @ivar argumentsByType: dictionary{Type, object}
        A dictionary containing as a key the argument type, this dictionary needs to be populated by the 
        processors with any system values that might be used for invoking, the actual use of this arguments depends
        on the invoking processor.
    '''
    __slots__ = ('invoker', 'arguments', 'argumentsByType')

    def __init__(self):
        '''
        Construct the invoke.
        '''
        self.invoker = None
        self.arguments = {}
        self.argumentsByType = {}

if __debug__:
    # Used to validate the values for the container in debug mode.
    validateTypeFor(Invoke, 'invoker', Invoker)
    validateTypeFor(Invoke, 'arguments', dict, False)
    validateTypeFor(Invoke, 'argumentsByType', dict, False)

class AdditionalArguments:
    '''
    Container for additional arguments.
    
    @ivar forType: dictionary{Type, object}
        A dictionary containing as a key the argument type, this dictionary needs to be populated by the 
        processors with any system values that might be used for invoking, the actual use of this arguments depends
        on the invoking processor.
    '''
    __slots__ = ('forType',)

    def __init__(self):
        '''
        Construct the invoke.
        '''
        self.forType = {}

if __debug__:
    # Used to validate the values for the container in debug mode.
    validateTypeFor(AdditionalArguments, 'forType', dict, False)

class Render:
    '''
    Container for rendering the response content.
    
    @ivar meta: Meta
        The meta object to be rendered.
    '''

    def __init__(self):
        '''
        Constructs the rendering.
        '''
        self.meta = None

if __debug__:
    # Used to validate the values for the container in debug mode.
    validateTypeFor(Render, 'meta', Meta)
