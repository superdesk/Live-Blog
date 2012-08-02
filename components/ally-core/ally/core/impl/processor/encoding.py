'''
Created on Jul 12, 2011

@package: ally core
@copyright: 2011 Sourcefabric o.p.s.
@license: http://www.gnu.org/licenses/gpl-3.0.txt
@author: Gabriel Nistor

Provides the encoding processing node.
'''

from ally.container.ioc import injected
from ally.core.spec.codes import UNKNOWN_ENCODING
from ally.core.spec.server import Processor, Request, Response, ProcessorsChain, \
    Processors
import logging
import codecs

# --------------------------------------------------------------------

log = logging.getLogger(__name__)

# --------------------------------------------------------------------

@injected
class EncodingProcessorsHandler(Processor):
    '''
    Implementation for a processor that provides the support for executing the encoding processors. The encoding
    just like decoding uses an internal processor chain execution. If a processor is successful in the encoding
    process it has to stop the chain execution.
    
    Provides on request: NA
    Provides on response: contentType
    
    Requires on request: accCharSets, accContentTypes
    Requires on response: [contentType]
    '''

    charSetDefault = str
    # The default character set to be used if none provided for the content.
    encodings = Processors
    # The encoding processors, if a processor is successful in the encoding process it has to stop the 
    # chain execution.

    def __init__(self):
        assert isinstance(self.encodings, Processors), 'Invalid encodings processors %s' % self.encodings
        assert isinstance(self.charSetDefault, str), 'Invalid default character set %s' % self.charSetDefault

    def process(self, req, rsp, chain):
        '''
        @see: Processor.process
        '''
        assert isinstance(req, Request), 'Invalid request %s' % req
        assert isinstance(rsp, Response), 'Invalid response %s' % rsp
        assert isinstance(chain, ProcessorsChain), 'Invalid processors chain %s' % chain

        # Resolving the character set
        if rsp.charSet:
            try: codecs.lookup(rsp.charSet)
            except LookupError: rsp.charSet = None
        if not rsp.charSet:
            for charSet in req.accCharSets:
                try: codecs.lookup(charSet)
                except LookupError: continue
                rsp.charSet = charSet
                break
            else: rsp.charSet = self.charSetDefault

        if rsp.contentType:
            encodingChain = self.encodings.newChain()
            assert isinstance(encodingChain, ProcessorsChain)
            encodingChain.process(req, rsp)
            if encodingChain.isConsumed():
                rsp.setCode(UNKNOWN_ENCODING,
                            'Content type %r not supported for encoding' % rsp.contentType)
                return
        else:
            contentTypes = list(req.accContentTypes)
            contentTypes.append(None) # Adding None in case some encoder is configured as default.
            for contentType in contentTypes:
                rsp.contentType = contentType
                encodingChain = self.encodings.newChain()
                assert isinstance(encodingChain, ProcessorsChain)
                encodingChain.process(req, rsp)
                if not encodingChain.isConsumed(): break
            else:
                rsp.setCode(UNKNOWN_ENCODING,
                        'Accepted content types %r not supported for encoding' % ', '.join(req.accContentTypes))
                return
        chain.proceed()
