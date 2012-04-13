'''
Created on Apr 13, 2012

@package: ally core
@copyright: 2011 Sourcefabric o.p.s.
@license: http://www.gnu.org/licenses/gpl-3.0.txt
@author: Gabriel Nistor

Provides the content decoding support.
'''

from ally.api.config import INSERT, UPDATE
from ally.api.model import Content
from ally.api.type import Input
from ally.container.ioc import injected
from ally.core.spec.resources import Invoker
from ally.core.spec.server import Request, Response, ProcessorsChain, \
    ContentRequest, Processor
import logging

# --------------------------------------------------------------------

log = logging.getLogger(__name__)

# --------------------------------------------------------------------

@injected
class DecodingContentHandler(Processor):
    '''
    Provides the decoder for JSON content.
    
    Provides on request: arguments
    Provides on response: NA
    
    Requires on request: method, invoker, content
    Requires on response: NA
    '''

    def process(self, req, rsp, chain):
        '''
        @see: Processor.process
        '''
        assert isinstance(req, Request), 'Invalid request %s' % req
        assert isinstance(rsp, Response), 'Invalid response %s' % rsp
        assert isinstance(chain, ProcessorsChain), 'Invalid processors chain %s' % chain
        assert req.method in (INSERT, UPDATE), 'Invalid method %s for processor' % req.method
        assert isinstance(req.content, ContentRequest), 'Invalid content on request %s' % req.content

        invoker = req.invoker
        assert isinstance(invoker, Invoker)
        if invoker.inputs:
            inp = invoker.inputs[invoker.mandatory - 1]
            assert isinstance(inp, Input)
            if inp.type.isOf(Content):
                req.arguments[inp.name] = req.content
                assert log.debug('Successfully provided content for input (%s)', inp.name) or True
                return
            else:
                assert log.debug('Expected a content input, could not find one') or True
        else:
            assert log.debug('Invalid request for the content decoder') or True
        chain.proceed()
