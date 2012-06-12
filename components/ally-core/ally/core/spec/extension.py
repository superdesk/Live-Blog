'''
Created on Jun 1, 2012

@package: ally core
@copyright: 2012 Sourcefabric o.p.s.
@license: http://www.gnu.org/licenses/gpl-3.0.txt
@author: Gabriel Nistor

Contains the extension classes for the server request/response.
'''

from ally.api.type import Type
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

class CharConvertId:
    '''
    The container with string transformation services that has an additional id converter.
    
    @ivar converterId: Converter
        The converter to use for model id's.
    '''
    __slots__ = ('converterId',)

    def __init__(self):
        '''
        Construct the id conversion container.
        '''
        self.converterId = None

if __debug__:
    # Used to validate the values for the container in debug mode.
    validateTypeFor(CharConvertId, 'converterId', Converter)

class Language:
    '''
    Container for text content language.
    
    @ivar language: string
        The language for the content.
    '''
    __slots__ = ('language',)

    def __init__(self):
        '''
        Construct the language specifications.
        '''
        self.language = None

if __debug__:
    # Used to validate the values for the container in debug mode.
    validateTypeFor(Language, 'language', str)

class LanguagesAccepted:
    '''
    Container for accepted content languages.
    
    @ivar accLanguages: list[string]
        The languages accepted for response.
    '''
    __slots__ = ('accLanguages',)

    def __init__(self):
        '''
        Construct the accepted content languages.
        '''
        self.accLanguages = []

if __debug__:
    # Used to validate the values for the container in debug mode.
    validateTypeFor(LanguagesAccepted, 'accLanguages', list, False)

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
    '''
    __slots__ = ('invoker',)

    def __init__(self):
        '''
        Construct the invoke.
        '''
        self.invoker = None

if __debug__:
    # Used to validate the values for the container in debug mode.
    validateTypeFor(Invoke, 'invoker', Invoker)

class Arguments:
    '''
    Container for invoking arguments.
    
    @ivar arguments: dictionary{string, object}
        A dictionary containing as a key the argument name, this dictionary needs to be populated by the 
        processors as seen fit, also the parameters need to be transformed to arguments.
    '''
    __slots__ = ('arguments',)

    def __init__(self):
        '''
        Construct the invoke.
        '''
        self.arguments = {}

if __debug__:
    # Used to validate the values for the container in debug mode.
    validateTypeFor(Arguments, 'arguments', dict, False)

class ArgumentsAdditional:
    '''
    Container for additional arguments.
    
    dictionary{Type, object}
        A dictionary containing as a key the argument type, this dictionary needs to be populated by the 
        processors with any system values that might be used for invoking, the actual use of this arguments depends
        on the invoking processor.
    '''
    __slots__ = ('argumentsOfType',)

    def __init__(self):
        '''
        Construct the invoke.
        '''
        self.argumentsOfType = {}

if __debug__:
    # Used to validate the values for the container in debug mode.
    validateTypeFor(ArgumentsAdditional, 'argumentsOfType', dict, False)

class ContructMeta:
    '''
    Container for constructing the meta for a provided type.
    
    @ivar metaForType: Type
        The type to construct the meta for.
    '''
    __slots__ = ('metaForType',)

    def __init__(self):
        '''
        Constructs the container.
        '''
        self.metaForType = None

if __debug__:
    # Used to validate the values for the container in debug mode.
    validateTypeFor(ContructMeta, 'metaForType', Type)

class RenderMeta:
    '''
    Container for rendering the response content.
    
    @ivar meta: Meta
        The meta object to be rendered.
    '''
    __slots__ = ('meta',)

    def __init__(self):
        '''
        Constructs the rendering.
        '''
        self.meta = None

if __debug__:
    # Used to validate the values for the container in debug mode.
    validateTypeFor(RenderMeta, 'meta', Meta)
