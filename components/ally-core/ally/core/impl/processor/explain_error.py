'''
Created on Jun 28, 2011

@package: Newscoop
@copyright: 2011 Sourcefabric o.p.s.
@license: http://www.gnu.org/licenses/gpl-3.0.txt
@author: Mihai Balaceanu

Provides support for explaining the errors in the content of the request.
'''

from ally.container.ioc import injected
from ally.core.spec.resources import Converter
from ally.core.spec.server import Response, Processor, ProcessorsChain, \
    Processors
from ally.exception import InputException, Ref
import logging

# --------------------------------------------------------------------

log = logging.getLogger(__name__)

# --------------------------------------------------------------------

@injected
class ExplainErrorHandler(Processor):
    '''
    Implementation for a processor that provides on the response a form of the error that can be extracted from 
    the response code and error message, this processor uses the code status (success) in order to trigger the error
    response.
    
    Provides on request: NA
    Provides on response: obj, objType, contentLocation, contentType, contentLanguage, contentConverter
    
    Requires on request: NA
    Requires on response: code
    '''
    
    encodings = Processors
    # The encoding processors used for presenting the error, if a processor is successful in the encoding 
    # process it has to stop the chain execution.
    languageDefault = str
    # The default language to use, if none available
    contentConverterDefault = Converter
    # The converter used by default if none is fount on the response.
    
    def __init__(self):
        assert isinstance(self.encodings, Processors), 'Invalid encodings processors %s' % self.encodings
        assert isinstance(self.languageDefault, str), 'Invalid string %s' % self.languageDefault
        assert isinstance(self.contentConverterDefault, Converter), \
        'Invalid content Converter object %s' % self.contentConverterDefault

    def process(self, req, rsp, chain):
        '''
        @see: Processor.process
        '''
        assert isinstance(rsp, Response), 'Invalid response %s' % rsp
        assert isinstance(chain, ProcessorsChain), 'Invalid processors chain %s' % chain
        chain.process(req, rsp)
        if not rsp.code.isSuccess:
            messages = []
            error = {'code':str(rsp.code.code)}
            if isinstance(rsp.codeMessage, str):
                messages.append(rsp.codeMessage)
            elif isinstance(rsp.codeMessage, InputException):
                iexc = rsp.codeMessage
                assert isinstance(iexc, InputException)
                for msg in iexc.message:
                    assert isinstance(msg, Ref)
                    messages.append(msg.message)
            if messages: error['message'] = messages
            rsp.obj = {'error':error}
            rsp.objType = None
            rsp.objMeta = None
            rsp.contentType = None
            rsp.contentLocation = None
            if not rsp.contentConverter:
                rsp.contentConverter = self.contentConverterDefault
            encodingChain = self.encodings.newChain()
            assert isinstance(encodingChain, ProcessorsChain)
            encodingChain.process(req, rsp)
