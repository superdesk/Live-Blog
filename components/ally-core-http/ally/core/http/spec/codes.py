'''
Created on Jun 1, 2012

@package: ally core http
@copyright: 2012 Sourcefabric o.p.s.
@license: http://www.gnu.org/licenses/gpl-3.0.txt
@author: Gabriel Nistor

Contains the codes to be used for the HTTP server responses.
'''

from ally.core.spec.codes import Code

# --------------------------------------------------------------------
# Response HTTP codes.

MISSING_HEADER = Code(400, False) # HTTP code 400 Bad Request
INVALID_HEADER_VALUE = Code(400, False) # HTTP code 400 Bad Request
INVALID_FORMATING = Code(400, False) # HTTP code 400 Bad Request
UNKNOWN_CONTENT_LENGHT = Code(411, False) # HTTP code 411 length required 
UNKNOWN_CONTENT_TYPE = Code(406, False) # HTTP code 406 Not acceptable
UNKNOWN_CHARSET = Code(406, False) # HTTP code 406 Not acceptable
UNKNOWN_PROPERTY = Code(400, False) # HTTP code 400 Bad Request
UNAUTHORIZED = Code(401 , False) # HTTP code 401 Unauthorized
