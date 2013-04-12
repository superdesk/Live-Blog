'''
Created on Jun 30, 2011

@package: ally core
@copyright: 2012 Sourcefabric o.p.s.
@license: http://www.gnu.org/licenses/gpl-3.0.txt
@author: Gabriel Nistor

Contains the codes to be used for the server responses.
'''

from ally.support.util import tupleify

# --------------------------------------------------------------------

@tupleify('code', 'isSuccess')
class Code:
    '''
    Contains the response code.
    '''

    def __init__(self, code, isSuccess):
        '''
        Constructs the code.
        
        @param code: string
            The code text corresponding to this code.
        @param isSuccess: boolean
            Flag indicating if the code is a fail or success code.
        '''
        assert isinstance(code, str), 'Invalid code %s' % code
        assert isinstance(isSuccess, bool), 'Invalid success flag %s' % isSuccess
        self.code = code
        self.isSuccess = isSuccess
        
# --------------------------------------------------------------------
# Response codes.

ENCODING_UNKNOWN = Code('Unknown encoding', False)

CONTENT_BAD = Code('Bad content', False)
CONTENT_ILLEGAL = Code('Illegal content', False)
CONTENT_MISSING = Code('Content missing', False)
CONTENT_EXPECTED = Code('Content stream expected', False)

INPUT_ERROR = Code('Input error', False)

DELETE_ERROR = Code('Cannot delete', False)
DELETE_SUCCESS = Code('Successfully deleted', True)

UPDATE_ERROR = Code('Cannot update', False)
UPDATE_SUCCESS = Code('Successfully updated', True)

INSERT_ERROR = Code('Cannot insert', False)
INSERT_SUCCESS = Code('Successfully inserted', True) 

