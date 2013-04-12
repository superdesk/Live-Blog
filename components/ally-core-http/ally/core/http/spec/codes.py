'''
Created on Jun 1, 2012

@package: ally core http
@copyright: 2012 Sourcefabric o.p.s.
@license: http://www.gnu.org/licenses/gpl-3.0.txt
@author: Gabriel Nistor

Contains the codes to be used for the HTTP server responses.
'''

from ally.core.spec.codes import ENCODING_UNKNOWN, CONTENT_BAD, CONTENT_ILLEGAL, \
    CONTENT_MISSING, CONTENT_EXPECTED, INPUT_ERROR, DELETE_ERROR, DELETE_SUCCESS, \
    UPDATE_ERROR, UPDATE_SUCCESS, INSERT_ERROR, INSERT_SUCCESS
from ally.http.spec.codes import CodeHTTP

# --------------------------------------------------------------------

# The mappings of error codes to HTTP status code
CODE_TO_STATUS = {
                  ENCODING_UNKNOWN.code: 400,  # HTTP code 400 Bad Request
                  CONTENT_BAD.code: 400,  # HTTP code 400 Bad Request
                  CONTENT_ILLEGAL.code: 400,  # HTTP code 400 Bad Request
                  CONTENT_MISSING.code: 400,  # HTTP code 400 Bad Request
                  CONTENT_EXPECTED.code: 400,  # HTTP code 400 Bad Request
                  INPUT_ERROR.code: 400,  # HTTP code 400 Bad Request
                  DELETE_ERROR.code: 400,  # HTTP code 404 Not Found
                  DELETE_SUCCESS.code: 204,  # HTTP code 204 No Content
                  UPDATE_ERROR.code: 400,  # HTTP code 404 Not Found
                  UPDATE_SUCCESS.code: 200,  # HTTP code 200 OK
                  INSERT_ERROR.code: 400,  # HTTP code 404 Not Found
                  INSERT_SUCCESS.code: 201,  # HTTP code 201 Created
                  }

# The mappings of error codes to HTTP status code
CODE_TO_TEXT = {
                CONTENT_EXPECTED.code: 'Required multipart request',
                }  

# --------------------------------------------------------------------
# Response HTTP codes.

MUTLIPART_ERROR = CodeHTTP('Invalid multipart', 400, False)  # HTTP code 400 Bad Request
MUTLIPART_NO_BOUNDARY = CodeHTTP('No boundary found in multipart content', 400, False)  # HTTP code 400 Bad Request

CONTENT_LENGHT_ERROR = CodeHTTP('Length required ', 411, False)  # HTTP code 411 length required 
CONTENT_TYPE_ERROR = CodeHTTP('Content type not acceptable ', 406, False)  # HTTP code 406 Not acceptable

PARAMETER_ILLEGAL = CodeHTTP('Illegal parameter', 400, False)  # HTTP code 400 Bad Request

FORMATING_ERROR = CodeHTTP('Invalid formatting', 400, False)  # HTTP code 400 Bad Request

TIME_ZONE_ERROR = CodeHTTP('Invalid time zone', 400, False)  # HTTP code 400 Bad Request

REDIRECT = CodeHTTP('Redirect', 302, True)  # HTTP code 302 originally temporary redirect, but now commonly used to specify redirection
# for unspecified reason
