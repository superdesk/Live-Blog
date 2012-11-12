'''
Created on Aug 24, 2012

@package: ally core
@copyright: 2011 Sourcefabric o.p.s.
@license: http://www.gnu.org/licenses/gpl-3.0.txt
@author: Gabriel Nistor

Provides the parsing chain processors.
'''

from ally.container.ioc import injected
from ally.core.spec.codes import UNKNOWN_ENCODING, Code
from ally.design.context import Context, defines, requires
from ally.design.processor import Assembly, Handler, Processing, \
    NO_MISSING_VALIDATION, Chain, Function
from collections import Callable
import codecs

# --------------------------------------------------------------------

class Request(Context):
    '''
    The request context.
    '''
    # ---------------------------------------------------------------- Required
    decoder = requires(Callable)

class RequestContent(Context):
    '''
    The request content context.
    '''
    # ---------------------------------------------------------------- Required
    type = requires(str)
    charSet = requires(str)

class Response(Context):
    '''
    The response context.
    '''
    # ---------------------------------------------------------------- Defined
    code = defines(Code)
    text = defines(str)

class ResponseContent(Context):
    '''
    The response context.
    '''
    # ---------------------------------------------------------------- Required
    type = requires(str)

# --------------------------------------------------------------------

@injected
class ParsingHandler(Handler):
    '''
    Implementation for a processor that provides the parsing based on contained parsers. If a parser
    processor is successful in the parsing process it has to stop the chain execution.
    '''

    charSetDefault = str
    # The default character set to be used if none provided for the content.
    parsingAssembly = Assembly
    # The parsers processors, if a processor is successful in the parsing process it has to stop the chain execution.

    def __init__(self, request=Request, requestCnt=RequestContent, response=Response, responseCnt=ResponseContent):
        assert isinstance(self.parsingAssembly, Assembly), 'Invalid parsers assembly %s' % self.parsingAssembly
        assert isinstance(self.charSetDefault, str), 'Invalid default character set %s' % self.charSetDefault

        parsingProcessing = self.parsingAssembly.create(NO_MISSING_VALIDATION, request=request, requestCnt=requestCnt,
                                                        response=response, responseCnt=responseCnt)
        assert isinstance(parsingProcessing, Processing), 'Invalid processing %s' % parsingProcessing
        super().__init__(Function(parsingProcessing.contexts, self.process))

        self.parsingProcessing = parsingProcessing

    def process(self, chain, request, requestCnt, response, **keyargs):
        '''
        Parse the request content.
        '''
        assert isinstance(chain, Chain), 'Invalid processors chain %s' % chain
        assert isinstance(request, Request), 'Invalid request %s' % request
        assert isinstance(response, Response), 'Invalid response %s' % response

        chain.proceed()

        if Response.code in response and not response.code.isSuccess: return # Skip in case the response is in error
        if Request.decoder not in request: return # Skip if there is no decoder.

        if self.processParsing(request=request, requestCnt=requestCnt, response=response, **keyargs):
            # We process the chain without the request content anymore
            chain.update(requestCnt=None)

    def processParsing(self, request, requestCnt, response, responseCnt, **keyargs):
        '''
        Process the parsing for the provided contexts.
        
        @return: boolean
            True if the parsing has been successfully done on the request content.
        '''
        assert isinstance(request, Request), 'Invalid request %s' % request
        assert isinstance(requestCnt, RequestContent), 'Invalid request content %s' % requestCnt
        assert isinstance(response, Response), 'Invalid response %s' % response
        assert isinstance(responseCnt, ResponseContent), 'Invalid response content %s' % responseCnt

        # Resolving the character set
        if RequestContent.charSet in requestCnt:
            try: codecs.lookup(requestCnt.charSet)
            except LookupError: requestCnt.charSet = self.charSetDefault
        else: requestCnt.charSet = self.charSetDefault
        if RequestContent.type not in requestCnt: requestCnt.type = responseCnt.type

        chain = Chain(self.parsingProcessing)
        chain.process(request=request, requestCnt=requestCnt, response=response, responseCnt=responseCnt, **keyargs)
        if not chain.doAll().isConsumed(): return True
        if Response.code not in response or response.code.isSuccess:
            response.code = UNKNOWN_ENCODING
            response.text = 'Content type \'%s\' not supported for parsing' % requestCnt.type
