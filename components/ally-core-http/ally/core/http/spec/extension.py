'''
Created on Jun 1, 2012

@package: ally core http
@copyright: 2012 Sourcefabric o.p.s.
@license: http://www.gnu.org/licenses/gpl-3.0.txt
@author: Gabriel Nistor

Contains the extension classes for the server request/response.
'''

from ally.core.http.spec.server import IEncoderPath, IDecoderHeader, \
    IEncoderHeader
from ally.support.util_sys import validateTypeFor

# --------------------------------------------------------------------

class Headers:
    '''
    Provides headers.
    
    @ivar headers: dictionary{string, string}
        The raw headers.
    '''
    __slots__ = ('headers',)

    def __init__(self):
        '''
        Construct the headers support.
        '''
        self.headers = {}

if __debug__:
    # Used to validate the values for the container in debug mode.
    validateTypeFor(Headers, 'headers', dict, False)

class URI:
    '''
    Container for URL data.
    
    @ivar scheme: string
        The scheme URI protocol name to be used for the response.
    @ivar uriRoot: string
        The root URI to be considered for constructing a request path, basically the relative path root.
    @ivar uri: string
        The relative request URI.
    @ivar parameters: list[tuple(string, string)]
        A list of tuples containing on the first position the parameter string name and on the second the string
        parameter value as provided in the request path. The parameters need to be transformed into arguments
        and also removed from this list while doing that.
        I did not use a dictionary on this since the parameter names might repeat and also the order might be
        important.
    '''
    __slots__ = ('scheme', 'uriRoot', 'uri', 'parameters')

    def __init__(self):
        '''
        Construct the URL container
        '''
        self.scheme = None
        self.uriRoot = None
        self.uri = None
        self.parameters = []

if __debug__:
    # Used to validate the values for the container in debug mode.
    validateTypeFor(URI, 'scheme', str)
    validateTypeFor(URI, 'uriRoot', str)
    validateTypeFor(URI, 'uri', str)
    validateTypeFor(URI, 'parameters', list, False)

class ContentType:
    '''
    The content type specification.
    
    @ivar typeAttr: dictionary{string, string}
        The content type attributes.
    '''
    __slots__ = ('typeAttr')

    def __init__(self):
        '''
        Construct the content type.
        '''
        self.typeAttr = {}

if __debug__:
    # Used to validate the values for the container in debug mode.
    validateTypeFor(ContentType, 'typeAttr', dict, False)

class ContentDisposition:
    '''
    The content disposition specification.
    
    @ivar disposition: string
        The content disposition.
    @ivar dispositionAttr: dictionary{string, string}
        The content disposition attributes.
    '''
    __slots__ = ('disposition', 'dispositionAttr')

    def __init__(self):
        '''
        Construct the content disposition.
        '''
        self.disposition = None
        self.dispositionAttr = {}

if __debug__:
    # Used to validate the values for the container in debug mode.
    validateTypeFor(ContentDisposition, 'disposition', str)
    validateTypeFor(ContentDisposition, 'dispositionAttr', dict, False)

# --------------------------------------------------------------------

class HTTPDecode:
    '''
    Provides the HTTP support decode services.
    
    @ivar decoderHeader: IDecoderHeader
        The decoder used for reading the headers.
    '''
    __slots__ = ('decoderHeader',)

    def __init__(self):
        '''
        Construct the HTTP support.
        '''
        self.decoderHeader = None

if __debug__:
    # Used to validate the values for the container in debug mode.
    validateTypeFor(HTTPDecode, 'decoderHeader', IDecoderHeader)

class HTTPEncode:
    '''
    Provides the HTTP support encode services.
    
    @ivar encoderHeader: IEncoderHeader
        The encoder used for setting the headers.
    @ivar encoderPath: IEncoderPath
        The path encoder used for encoding paths that will be rendered in the response.
    '''
    __slots__ = ('encoderHeader', 'encoderPath')

    def __init__(self):
        '''
        Construct the HTTP support.
        '''
        self.encoderHeader = None
        self.encoderPath = None

if __debug__:
    # Used to validate the values for the container in debug mode.
    validateTypeFor(HTTPEncode, 'encoderHeader', IEncoderHeader)
    validateTypeFor(HTTPEncode, 'encoderPath', IEncoderPath)
