'''
Created on Jun 11, 2012

@package: ally core http
@copyright: 2012 Sourcefabric o.p.s.
@license: http://www.gnu.org/licenses/gpl-3.0.txt
@author: Gabriel Nistor

Provides the allow headers handling.
'''

from ally.api.config import GET, DELETE, INSERT, UPDATE
from ally.container.ioc import injected
from ally.core.http.spec.server import IEncoderHeader
from ally.design.processor import Handler, Chain, processor
from ally.design.context import Context, requires

# --------------------------------------------------------------------

class Response(Context):
    '''
    The response context.
    '''
    # ---------------------------------------------------------------- Required
    allows = requires(int)
    encoderHeader = requires(IEncoderHeader)

# --------------------------------------------------------------------

@injected
class AllowHandler(Handler):
    '''
    Implementation for a processor that provides the encoding of allow HTTP request headers.
    '''

    nameAllow = 'Allow'
    # The allow header name
    methodsAllow = ((GET, 'GET'), (DELETE, 'DELETE'), (INSERT, 'POST'), (UPDATE, 'PUT'))
    # The mapping between method mark and method name, we used a tuple instead of a dictionary to have a proper
    # order of the method names when rendering the value of the header.

    def __init__(self):
        assert isinstance(self.nameAllow, str), 'Invalid allow name %s' % self.nameAllow
        assert isinstance(self.methodsAllow, (list, tuple)), 'Invalid methods allow %s' % self.methodsAllow

    @processor
    def encode(self, chain, response:Response, **keyargs):
        '''
        Encode the allow headers.
        '''
        assert isinstance(chain, Chain), 'Invalid processors chain %s' % chain
        assert isinstance(response, Response), 'Invalid response %s' % response
        assert isinstance(response.encoderHeader, IEncoderHeader), \
        'Invalid response header encoder %s' % response.encoderHeader

        if Response.allows in response and response.allows != 0:
            value = [name for mark, name in self.methodsAllow if response.allows & mark != 0]
            response.encoderHeader.encode(self.nameAllow, *value)

        chain.proceed()
