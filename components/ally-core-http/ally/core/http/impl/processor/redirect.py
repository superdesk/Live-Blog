'''
Created on Apr 12, 2012

@package: ally core
@copyright: 2011 Sourcefabric o.p.s.
@license: http://www.gnu.org/licenses/gpl-3.0.txt
@author: Gabriel Nistor

Provides the content location redirect based on references.
'''

from ally.api.operator.type import TypeModelProperty
from ally.api.type import TypeReference
from ally.container.ioc import injected
from ally.core.http.spec.server import IEncoderPath, IEncoderHeader
from ally.core.spec.codes import REDIRECT, Code
from ally.core.spec.resources import Invoker
from ally.design.context import Context, requires, defines
from ally.design.processor import Handler, Assembly, NO_VALIDATION, Processing, \
    Chain, Processor
from functools import partial
import logging

# --------------------------------------------------------------------

log = logging.getLogger(__name__)

# --------------------------------------------------------------------

class Request(Context):
    '''
    The request context.
    '''
    # ---------------------------------------------------------------- Required
    invoker = requires(Invoker)

class Response(Context):
    '''
    The response context.
    '''
    # ---------------------------------------------------------------- Required
    encoderHeader = requires(IEncoderHeader)
    encoderPath = requires(IEncoderPath)
    obj = requires(object)
    # ---------------------------------------------------------------- Defined
    code = defines(Code)
    text = defines(str)

# --------------------------------------------------------------------

@injected
class RedirectHandler(Handler):
    '''
    Implementation for a processor that provides the redirect by using the content location based on found references.
    '''

    nameLocation = 'Location'
    # The header name for the location redirect.
    redirectAssembly = Assembly
    # The redirect processors, among this processors it has to be one to fetch the location object.

    def __init__(self):
        assert isinstance(self.redirectAssembly, Assembly), 'Invalid redirect assembly %s' % self.redirectAssembly
        assert isinstance(self.nameLocation, str), 'Invalid string %s' % self.nameLocation

        redirectProcessing = self.redirectAssembly.create(NO_VALIDATION, request=Request, response=Response)
        assert isinstance(redirectProcessing, Processing), 'Invalid processing %s' % redirectProcessing

        super().__init__(Processor(redirectProcessing.contexts, partial(self.process, redirectProcessing),
                                   'process', self.process.__code__.co_filename, self.process.__code__.co_firstlineno))

    def process(self, redirectProcessing, chain, request, response, **keyargs):
        '''
        Process the redirect.
        
        @param redirectProcessing: Processing
            The processing that provides the redirecting chain.
            
        The rest of the parameters are contexts.
        '''
        assert isinstance(redirectProcessing, Processing), 'Invalid redirect processing %s' % redirectProcessing
        assert isinstance(chain, Chain), 'Invalid processors chain %s' % chain
        assert isinstance(request, Request), 'Invalid request %s' % request
        assert isinstance(response, Response), 'Invalid response %s' % response

        if Response.code not in response or response.code.isSuccess: # Skip in case the response is in error
            assert isinstance(request.invoker, Invoker), 'Invalid request invoker %s' % request.invoker

            typ = request.invoker.output
            if isinstance(typ, TypeModelProperty): typ = typ.type
            if isinstance(typ, TypeReference):
                redirectChain = Chain(redirectProcessing)
                redirectChain.process(request=request, response=response, **keyargs).doAll()
                if Response.code not in response or response.code.isSuccess:
                    assert isinstance(response.encoderHeader, IEncoderHeader), \
                    'Invalid header encoder %s' % response.encoderHeader
                    assert isinstance(response.encoderPath, IEncoderPath), \
                    'Invalid encoder path %s' % response.encoderPath

                    response.encoderHeader.encode(self.nameLocation, response.encoderPath.encode(response.obj))
                    response.code, response.text = REDIRECT, 'Redirect'
                    return

        chain.proceed()
