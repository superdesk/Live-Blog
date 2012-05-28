'''
Created on Jun 30, 2011

@package: ally core
@copyright: 2012 Sourcefabric o.p.s.
@license: http://www.gnu.org/licenses/gpl-3.0.txt
@author: Gabriel Nistor

Contains the codes to be used for the server responses.
'''

# --------------------------------------------------------------------

class Code:
    '''
    Contains the server code.
    '''

    def __init__(self, code, isSuccess):
        '''
        Constructs the code.
        
        @param code: integer
            The integer code corresponding to this code.
        @param isSuccess: boolean
            Flag indicating if the code is a fail or success code.
        '''
        assert isinstance(code, int), 'Invalid code %s' % code
        assert isinstance(isSuccess, bool), 'Invalid success flag %s' % isSuccess
        self.code = code
        self.isSuccess = isSuccess

# --------------------------------------------------------------------
# Response codes.
UNKNOWN_ENCODING = Code(400, False) # HTTP code 400 Bad Request
UNKNOWN_DECODING = Code(400, False) # HTTP code 400 Bad Request
UNKNOWN_FORMAT = Code(400, False) # HTTP code 400 Bad Request
UNKNOWN_LANGUAGE = Code(400, False) # HTTP code 400 Bad Request
INVALID_FORMATING = Code(400, False) # HTTP code 400 Bad Request
BAD_CONTENT = Code(400, False) # HTTP code 400 Bad Request
ILLEGAL_PARAM = Code(400, False) # HTTP code 400 Bad Request
RESOURCE_NOT_FOUND = Code(404, False) # HTTP code 404 Not Found
METHOD_NOT_AVAILABLE = Code(501, False) # HTTP code 501 Unsupported method
CANNOT_DELETE = Code(404, False) # HTTP code 404 Not Found
CANNOT_UPDATE = Code(404, False) # HTTP code 404 Not Found
CANNOT_INSERT = Code(404, False) # HTTP code 404 Not Found
INTERNAL_ERROR = Code(500, False) # HTTP code 500 Internal Server Error

RESOURCE_FOUND = Code(200, True) # HTTP code 200 OK
REDIRECT = Code(302, True) # HTTP code 302 originally temporary redirect, but now commonly used to specify redirection
# for unspecified reason
DELETED_SUCCESS = Code(204, True) # HTTP code 204 No Content
UPDATE_SUCCESS = Code(200, True) # HTTP code 200 OK
INSERT_SUCCESS = Code(201, True) # HTTP code 201 Created
