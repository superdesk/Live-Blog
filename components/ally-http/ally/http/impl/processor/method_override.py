'''
Created on Aug 9, 2011

@package: ally http
@copyright: 2012 Sourcefabric o.p.s.
@license: http://www.gnu.org/licenses/gpl-3.0.txt
@author: Gabriel Nistor

Provides the method override header handling.
'''

from ally.container.ioc import injected
from ally.design.processor.attribute import requires, defines
from ally.design.processor.context import Context
from ally.design.processor.handler import HandlerProcessorProceed
from ally.http.spec.codes import HEADER_ERROR
from ally.http.spec.server import IDecoderHeader, HTTP_GET, HTTP_POST, \
    HTTP_DELETE, HTTP_PUT
import logging

# --------------------------------------------------------------------

log = logging.getLogger(__name__)

# --------------------------------------------------------------------

class Request(Context):
    '''
    The request context.
    '''
    # ---------------------------------------------------------------- Required
    decoderHeader = requires(IDecoderHeader)
    method = requires(str)

class Response(Context):
    '''
    The response context.
    '''
    # ---------------------------------------------------------------- Defined
    code = defines(str)
    status = defines(int)
    isSuccess = defines(bool)
    text = defines(str)

# --------------------------------------------------------------------

@injected
class MethodOverrideHandler(HandlerProcessorProceed):
    '''
    Provides the method override processor.
    '''

    nameXMethodOverride = 'X-HTTP-Method-Override'
    # The header name for the method override.
    methodsOverride = {
                       HTTP_GET: [HTTP_DELETE],
                       HTTP_POST: [HTTP_PUT],
                       }
    # A dictionary containing as a key the original method and as a value the methods that are allowed for override.

    def __init__(self):
        assert isinstance(self.nameXMethodOverride, str), 'Invalid method override name %s' % self.nameXMethodOverride
        assert isinstance(self.methodsOverride, dict), 'Invalid methods override %s' % self.methodsOverride
        super().__init__()

    def process(self, request:Request, response:Response, **keyargs):
        '''
        @see: HandlerProcessorProceed.process
        
        Overrides the request method based on a provided header.
        '''
        assert isinstance(request, Request), 'Invalid request %s' % request
        assert isinstance(response, Response), 'Invalid response %s' % response
        if response.isSuccess is False: return  # Skip in case the response is in error

        assert isinstance(request.decoderHeader, IDecoderHeader), 'Invalid header decoder %s' % request.decoderHeader

        value = request.decoderHeader.retrieve(self.nameXMethodOverride)
        if value:
            
            allowed = self.methodsOverride.get(request.method)
            if not allowed:
                response.code, response.status, response.isSuccess = HEADER_ERROR
                response.text = 'Cannot override method \'%s\'' % request.method
                return

            value = value.upper()
            if value not in allowed:
                response.code, response.status, response.isSuccess = HEADER_ERROR
                response.text = 'Cannot override method \'%s\' to method \'%s\'' % (request.method, value)
                return

            assert log.debug('Successfully overridden method %s with %s', request.method, value) or True
            request.method = value
