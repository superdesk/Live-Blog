'''
Created on Jul 12, 2011

@package: ally core
@copyright: 2011 Sourcefabric o.p.s.
@license: http://www.gnu.org/licenses/gpl-3.0.txt
@author: Gabriel Nistor

Provides the encoding processing node.
'''

from ally.container.ioc import injected
from ally.core.spec.codes import UNKNOWN_ENCODING, Code
from ally.design.context import Context, defines, optional
from ally.design.processor import Assembly, Handler, Processing, NO_VALIDATION, \
    Processor, Chain
from ally.exception import DevelError
import codecs
import itertools
from functools import partial

# --------------------------------------------------------------------

class Request(Context):
    '''
    The request context.
    '''
    # ---------------------------------------------------------------- Optional
    accTypes = optional(list)
    accCharSets = optional(list)

class Response(Context):
    '''
    The response context.
    '''
    # ---------------------------------------------------------------- Defined
    code = defines(Code)
    text = defines(str)
    type = defines(str, doc='''
    @rtype: string
    The response content type.
    ''')
    charSet = defines(str, doc='''
    @rtype: string
    The character set for the text content.
    ''')

# --------------------------------------------------------------------

@injected
class RendererHandler(Handler):
    '''
    Implementation for a processor that provides the support for creating the renderer. The renderer just like decoding
    uses an internal processor chain execution. If a processor is successful in the render creation process it has to
    stop the chain execution.
    '''

    contentTypeDefaults = [None]
    # The default content types to use
    charSetDefault = str
    # The default character set to be used if none provided for the content.
    renderAssembly = Assembly
    # The render processors, if a processor is successful in the rendering factory creation process it has to stop the 
    # chain execution.

    def __init__(self):
        assert isinstance(self.renderAssembly, Assembly), 'Invalid renders assembly %s' % self.renderAssembly
        assert isinstance(self.contentTypeDefaults, (list, tuple)), \
        'Invalid default content type %s' % self.contentTypeDefaults
        assert isinstance(self.charSetDefault, str), 'Invalid default character set %s' % self.charSetDefault

        renderProcessing = self.renderAssembly.create(NO_VALIDATION, request=Request, response=Response)
        assert isinstance(renderProcessing, Processing), 'Invalid processing %s' % renderProcessing

        super().__init__(Processor(renderProcessing.contexts, partial(self.process, renderProcessing), 'process',
                                   self.process.__code__.co_filename, self.process.__code__.co_firstlineno))

    def process(self, renderProcessing, chain, request, response, **keyargs):
        '''
        Encodes the response object.
        
        @param renderProcessing: Processing
            The processing that provides the rendering chain.
            
        The rest of the parameters are contexts.
        '''
        assert isinstance(renderProcessing, Processing), 'Invalid render processing %s' % renderProcessing
        assert isinstance(chain, Chain), 'Invalid processors chain %s' % chain
        assert isinstance(request, Request), 'Invalid request %s' % request
        assert isinstance(response, Response), 'Invalid response %s' % response

        # Resolving the character set
        if Response.charSet in response:
            try: codecs.lookup(response.charSet)
            except LookupError: response.charSet = None
        else: response.charSet = None

        if response.charSet is None:
            for charSet in request.accCharSets or ():
                try: codecs.lookup(charSet)
                except LookupError: continue
                response.charSet = charSet
                break
            else: response.charSet = self.charSetDefault

        resolved = False
        if Response.type in response:
            renderChain = renderProcessing.newChain()
            assert isinstance(renderChain, Chain), 'Invalid chain %s' % renderChain

            renderChain.process(request=request, response=response, **keyargs)
            if renderChain.isConsumed():
                if Response.code not in response or response.code.isSuccess:
                    response.code = UNKNOWN_ENCODING
                    response.text = 'Content type \'%s\' not supported for encoding' % response.type
            else: resolved = True

        if not resolved:
            # Adding None in case some encoder is configured as default.
            for contentType in itertools.chain(request.accTypes or (), self.contentTypeDefaults):
                response.type = contentType

                renderChain = renderProcessing.newChain()
                assert isinstance(renderChain, Chain), 'Invalid chain %s' % renderChain

                renderChain.process(request=request, response=response, **keyargs)
                if not renderChain.isConsumed(): break
            else:
                raise DevelError('There is no renderer available, this is more likely a setup issues since the '
                                 'default content types should have resolved the renderer')
        chain.proceed()
