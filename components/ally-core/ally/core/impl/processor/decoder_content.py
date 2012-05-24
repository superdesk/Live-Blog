'''
Created on Apr 13, 2012

@package: ally core
@copyright: 2011 Sourcefabric o.p.s.
@license: http://www.gnu.org/licenses/gpl-3.0.txt
@author: Gabriel Nistor

Provides the content decoding support.
'''

from ally.api.model import Content
from ally.api.operator.type import TypeModel
from ally.api.type import Input
from ally.container.ioc import injected
from ally.core.spec.codes import BAD_CONTENT
from ally.core.spec.resources import Invoker
from ally.core.spec.server import Request, Response, ProcessorsChain, \
    ContentRequest, IProcessor
import logging

# --------------------------------------------------------------------

log = logging.getLogger(__name__)

# --------------------------------------------------------------------

@injected
class DecodingContentHandler(IProcessor):
    '''
    Provides the decoder for JSON content.
    
    Provides on request: arguments
    Provides on response: NA
    
    Requires on request: invoker, content
    Requires on response: NA
    '''

    def process(self, req, rsp, chain):
        '''
        @see: IProcessor.process
        '''
        assert isinstance(req, Request), 'Invalid request %s' % req
        assert isinstance(rsp, Response), 'Invalid response %s' % rsp
        assert isinstance(chain, ProcessorsChain), 'Invalid processors chain %s' % chain
        assert isinstance(req.content, ContentRequest), 'Invalid content on request %s' % req.content

        invoker = req.invoker
        assert isinstance(invoker, Invoker)
        if invoker.inputs:
            inpContent = invoker.inputs[invoker.mandatory - 1]
            assert isinstance(inpContent, Input)
            if inpContent.type.isOf(Content):
                # So the last entry is a content model we need to see if there are any other models that require to
                # be decoded
                for k in range(0, invoker.mandatory - 1):
                    inp = invoker.inputs[k]
                    assert isinstance(inp, Input)
                    if isinstance(inp.type, TypeModel): break
                else:
                    # There is no model to be decoded so we just provide the entire content as the input
                    req.arguments[inpContent.name] = req.content
                    assert log.debug('Successfully provided entire content for input (%s)', inpContent.name) or True
                    return
                # If there is a type model object we need to get data to compose it, this will probably mean that the
                # content will have to have a next() content available.
                chain.process(req, rsp)
                # We process the rest of the decoding chain in the hope that a decoder will provide the models.
                if not chain.isConsumed() and rsp.code.isSuccess:
                    # If the chain is not consumed and the code is successful it definitely means that we had a successful
                    # model decoding, so now lets see about the content input.
                    content = req.content.next()
                    if not content:
                        rsp.setCode(BAD_CONTENT, 'Required a %s content follow up' % inpContent.name)
                        return
                    req.arguments[inpContent.name] = req.content = content
                    assert log.debug('Successfully provided the next content for input (%s)', inpContent.name) or True
                    return
            else:
                assert log.debug('Expected a content input, could not find one') or True
        else:
            assert log.debug('Invalid request for the content decoder') or True
        chain.proceed()
