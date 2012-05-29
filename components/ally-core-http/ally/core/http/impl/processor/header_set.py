'''
Created on Nov 15, 2011

@package: ally core http
@copyright: 2012 Sourcefabric o.p.s.
@license: http://www.gnu.org/licenses/gpl-3.0.txt
@author: Gabriel Nistor

Provides support for setting headers on responses.
'''

from ally.container.ioc import injected
from ally.core.http.spec import ResponseHTTP
from ally.core.spec.server import IProcessor, ProcessorsChain
import logging

# --------------------------------------------------------------------

log = logging.getLogger(__name__)

# --------------------------------------------------------------------

@injected
class HeaderSetHandler(IProcessor):
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

    def process(self, req, rsp, chain):
        '''
        @see: IProcessor.process
        '''
        assert isinstance(rsp, ResponseHTTP), 'Invalid response %s' % rsp
        assert isinstance(chain, ProcessorsChain), 'Invalid processors chain %s' % chain
        rsp.headers.update(self.headers)
        chain.proceed()
