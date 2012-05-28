'''
Created on Jul 8, 2011

@package: ally core http
@copyright: 2012 Sourcefabric o.p.s.
@license: http://www.gnu.org/licenses/gpl-3.0.txt
@author: Gabriel Nistor

Provides specifications for APIs used by the HTTP server.
'''

import abc
from ally.core.spec.server import Request, ContentRequest
from ally.core.spec.codes import Code
from collections import OrderedDict, deque

# --------------------------------------------------------------------

class RequestHTTP(Request):
    '''
    Provides the request extension with additional HTTP data.
    
    @ivar path: list[string]
        The split relative request path.
    @ivar headers: dictionary
        The headers of the request
    @ivar parameters: deque[tuple(string, string)]
        A list of tuples containing on the first position the parameter string name and on the second the string
        parameter value as provided in the request path. The parameters need to be transformed into arguments
        and also removed from this list while doing that.
        I did not use a dictionary on this since the parameter names might repeat and also the order might be
        important.
    @ivar rootURI: string
        The root URI to be considered for constructing a request path, basically the relative path root.
    '''
    path = list
    headers = dict
    parameters = deque
    rootURI = str

    def __init__(self):
        '''
        Construct the HTTP request.
        '''
        super().__init__()
        self.path = None
        self.headers = {}
        self.parameters = deque()
        self.rootURI = ''

class ContentRequestHTTP(ContentRequest):
    '''
    Provides the content request extension with additional HTTP data.
    '''

    def __init__(self):
        '''
        @see: ContentRequest.__init__
        
        @ivar contentTypeAttributes: dictionary{string, string}
            The content type extra attributes, this attributes will not include the standard attributes, for instance the
            character set.
        @ivar contentDisposition: string
            The content disposition for the request content if available.
        @ivar contentDispositionAttributes: dictionary{string, string}
            The content disposition extra attributes.
        '''
        super().__init__()
        self.contentTypeAttributes = OrderedDict()

# --------------------------------------------------------------------

class EncoderHeader(metaclass=abc.ABCMeta):
    '''
    Provides the API for encoding the headers from response.
    '''

    @abc.abstractmethod
    def encode(self, headers, response):
        '''
        Encode data from the response that is relevant for this encoder in the provided header dictionary.
        
        @param headers: dictionary
            The dictionary containing the headers, as a key the header name.
        @param response: Response
            The response to extract data for the headers from.
        '''

# --------------------------------------------------------------------
# Additional HTTP methods.

METHOD_OPTIONS = 16

# --------------------------------------------------------------------
# Response HTTP codes.

MISSING_HEADER = Code(400, False) # HTTP code 400 Bad Request
INVALID_HEADER_VALUE = Code(400, False) # HTTP code 400 Bad Request
UNKNOWN_CONTENT_LENGHT = Code(411, False) # HTTP code 411 length required 
UNKNOWN_CONTENT_TYPE = Code(406, False) # HTTP code 406 Not acceptable
UNKNOWN_CHARSET = Code(406, False) # HTTP code 406 Not acceptable
UNKNOWN_PROPERTY = Code(400, False) # HTTP code 400 Bad Request
UNAUTHORIZED = Code(401 , False) # HTTP code 401 Unauthorized
