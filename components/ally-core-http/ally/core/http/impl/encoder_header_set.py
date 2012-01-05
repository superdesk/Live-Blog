'''
Created on Nov 15, 2011

@package: Newscoop
@copyright: 2011 Sourcefabric o.p.s.
@license: http://www.gnu.org/licenses/gpl-3.0.txt
@author: Gabriel Nistor

Provides support for setting headers on responses.
'''

from ally.container.ioc import injected
from ally.core.http.spec import EncoderHeader
from ally.core.spec.server import Response
import logging

# --------------------------------------------------------------------

log = logging.getLogger(__name__)

# --------------------------------------------------------------------

@injected
class EncoderHeaderSet(EncoderHeader):
    '''
    Provides the setting of static header values.
    '''
    
    headers = dict
    # The static header values to set on the response.
   
    def __init__(self):
        assert isinstance(self.headers, dict), 'Invalid header dictionary %s' % self.header
        if __debug__:
            for name, value in self.headers.items():
                assert isinstance(name, str), 'Invalid header name %s' % name
                assert isinstance(value, str), 'Invalid header value %s' % value

    def encode(self, headers, rsp):
        '''
        @see: EncoderHeader.encode
        '''
        assert isinstance(headers, dict), 'Invalid headers dictionary %s' % headers
        assert isinstance(rsp, Response), 'Invalid response %s' % rsp
        headers.update(self.headers)
