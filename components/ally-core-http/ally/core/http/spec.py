'''
Created on Jul 8, 2011

@package: Newscoop
@copyright: 2011 Sourcefabric o.p.s.
@license: http://www.gnu.org/licenses/gpl-3.0.txt
@author: Gabriel Nistor

Provides specifications for APIs used by the HTTP server.
'''

import abc
from ally.core.spec.server import Request
from ally.core.spec.codes import Code

# --------------------------------------------------------------------

class RequestHTTP(Request):
    '''
    Provides the request extension with additional HTTP data.
    '''

    def __init__(self):
        '''
        @ivar path: string | list[string] | tuple(string)
            The relative requested path, or split relative request path.
        @ivar headers: dictionary
            The headers of the request
        @ivar rootURI: string | None
            The root URI to be considered for constructing a request path, basically the relative path root. None if the path
            is not relative.
        '''
        self.path = None
        self.headers = {}
        self.rootURI = None
        super().__init__()

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
