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
from ally.exception import InputError, Ref, DevelError
import logging
from ally.core.spec.codes import BAD_CONTENT, INTERNAL_ERROR

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

        process(chain, req, rsp)

        if not rsp.code.isSuccess:
            messages = []
            error = {'code':str(rsp.code.code)}
            if isinstance(rsp.codeMessage, str):
                messages.append(rsp.codeMessage)
            elif isinstance(rsp.codeMessage, InputError):
                iexc = rsp.codeMessage
                assert isinstance(iexc, InputError)
                for msg in iexc.message:
                    assert isinstance(msg, Ref)
                    messages.append(msg.message)
            if messages: error['message'] = ', '.join(messages)
            rsp.obj = {'error':error}
            rsp.objType = None
            rsp.objMeta = None
            rsp.contentType = None
            rsp.location = None
            if not rsp.contentConverter:
                rsp.contentConverter = self.contentConverterDefault
            encodingChain = self.encodings.newChain()
            assert isinstance(encodingChain, ProcessorsChain)
            encodingChain.process(req, rsp)

# --------------------------------------------------------------------

def process(chain, req, rsp):
    '''
    Processes the chain in a safe manner by catching any known or unknown exceptions.
    @see: Processor.process
    '''
    assert isinstance(rsp, Response), 'Invalid response %s' % rsp
    assert isinstance(chain, ProcessorsChain), 'Invalid processors chain %s' % chain

    try: chain.process(req, rsp)
    except DevelError as e:
        rsp.setCode(BAD_CONTENT, e.message)
        log.info('Problems with the invoked content: %s', e.message, exc_info=True)
    except InputError as e:
        rsp.setCode(BAD_CONTENT, e, 'Invalid resource')
        assert log.debug('User input exception: %s', e, exc_info=True) or True
    except:
        rsp.setCode(INTERNAL_ERROR, 'Upps, it seems I am in a pickle, please consult the server logs')
        log.exception('An exception occurred while trying to process request %s and response %s', req, rsp)
