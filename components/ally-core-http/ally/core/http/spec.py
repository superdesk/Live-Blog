'''
Created on Jul 8, 2011

@package: ally core http
@copyright: 2012 Sourcefabric o.p.s.
@license: http://www.gnu.org/licenses/gpl-3.0.txt
@author: Gabriel Nistor

Provides specifications for APIs used by the HTTP server.
'''

from ally.core.spec.server import Request, ContentRequest, Response
from ally.core.spec.codes import Code
from collections import OrderedDict, deque

# --------------------------------------------------------------------

class ContentRequestHTTP(ContentRequest):
    '''
    Provides the content request extension with additional HTTP data.
    '''
    __slots__ = ('contentTypeAttributes',)

    def __init__(self):
        '''
        @see: ContentRequest.__init__
        
        @ivar contentTypeAttributes: dictionary{string, string}
            The content type extra attributes, this attributes will not include the standard attributes, for instance the
            character set.
        '''
        super().__init__()
        self.contentTypeAttributes = OrderedDict()

class RequestHTTP(Request):
    '''
    Provides the request extension with additional HTTP data.
    '''
    __slots__ = ('path', 'headers', 'parameters', 'rootURI')

    def __init__(self):
        '''
        Construct the HTTP request.
    
        @ivar path: list[string]
            The split relative request path.
        @ivar headers: dictionary{string, string}
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
        super().__init__()
        self.path = None
        self.headers = {}
        self.parameters = deque()
        self.rootURI = ''

class ResponseHTTP(Response):
    '''
    Provides the response extension with additional HTTP data.
    '''
    __slots__ = ('headers',)

    def __init__(self):
        '''
        Construct the HTTP response.
    
        @ivar headers: dictionary{string, string}
            The headers for the response.
        '''
        super().__init__()
        self.headers = {}

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
