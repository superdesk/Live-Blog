'''
Created on Sep 20, 2011

@package: Newscoop
@copyright: 2011 Sourcefabric o.p.s.
@license: http://www.gnu.org/licenses/gpl-3.0.txt
@author: Gabriel Nistor

Provides the encoder/decoder whenever there is no content required for the invoker.
'''

from ally.container.ioc import injected
from ally.core.impl.processor.decoder_text_base import findLastModel
from ally.core.spec.server import IProcessor, Request, Response, ProcessorsChain
import logging
from ally.api.config import INSERT, UPDATE

# --------------------------------------------------------------------

log = logging.getLogger(__name__)

# --------------------------------------------------------------------

@injected
class DecodingNoneHandler(IProcessor):
    '''
    Provides the decoder for no content. Used in order to signal that there is no decoding need rather than a
    decoding problem.
    '''

    def process(self, req, rsp, chain):
        '''
        @see: IProcessor.process
        '''
        assert isinstance(req, Request), 'Invalid request %s' % req
        assert isinstance(rsp, Response), 'Invalid response %s' % rsp
        assert isinstance(chain, ProcessorsChain), 'Invalid processors chain %s' % chain
        assert req.method in (INSERT, UPDATE), 'Invalid method %s for processor' % req.method

        if not findLastModel(req.invoker): assert log.debug('Nothing required to be decoded for this invoking') or True
        else: chain.proceed()
