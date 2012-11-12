'''
Created on Jul 12, 2011

@package: ally core
@copyright: 2011 Sourcefabric o.p.s.
@license: http://www.gnu.org/licenses/gpl-3.0.txt
@author: Gabriel Nistor

Provides the rendering processing.
'''

from ally.container.ioc import injected
from ally.core.spec.codes import UNKNOWN_ENCODING, Code
from ally.design.context import Context, defines, optional
from ally.design.processor import Assembly, Handler, Processing, NO_VALIDATION, \
    Chain, Function
from ally.exception import DevelError
import codecs
import itertools

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

class ResponseContent(Context):
    '''
    The response content context.
    '''
    # ---------------------------------------------------------------- Defined
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
class RenderingHandler(Handler):
    '''
    Implementation for a processor that provides the support for creating the renderer. If a processor is successful
    in the render creation process it has to stop the chain execution.
    '''

    contentTypeDefaults = [None]
    # The default content types to use
    charSetDefault = str
    # The default character set to be used if none provided for the content.
    renderingAssembly = Assembly
    # The render processors, if a processor is successful in the rendering factory creation process it has to stop the 
    # chain execution.

    def __init__(self):
        assert isinstance(self.renderingAssembly, Assembly), 'Invalid renders assembly %s' % self.renderingAssembly
        assert isinstance(self.contentTypeDefaults, (list, tuple)), \
        'Invalid default content type %s' % self.contentTypeDefaults
        assert isinstance(self.charSetDefault, str), 'Invalid default character set %s' % self.charSetDefault

        renderingProcessing = self.renderingAssembly.create(NO_VALIDATION, request=Request,
                                                            response=Response, responseCnt=ResponseContent)
        assert isinstance(renderingProcessing, Processing), 'Invalid processing %s' % renderingProcessing
        super().__init__(Function(renderingProcessing.contexts, self.process))

        self.renderingProcessing = renderingProcessing

    def process(self, chain, request, response, responseCnt, **keyargs):
        '''
        Create the render for the response object.
        '''
        assert isinstance(chain, Chain), 'Invalid processors chain %s' % chain
        assert isinstance(request, Request), 'Invalid request %s' % request
        assert isinstance(response, Response), 'Invalid response %s' % response
        assert isinstance(responseCnt, ResponseContent), 'Invalid response content %s' % responseCnt

        chain.proceed()
        
        # Resolving the character set
        if ResponseContent.charSet in responseCnt:
            try: codecs.lookup(responseCnt.charSet)
            except LookupError: responseCnt.charSet = None
        else: responseCnt.charSet = None

        if responseCnt.charSet is None:
            for charSet in request.accCharSets or ():
                try: codecs.lookup(charSet)
                except LookupError: continue
                responseCnt.charSet = charSet
                break
            else: responseCnt.charSet = self.charSetDefault

        resolved = False
        if ResponseContent.type in responseCnt:
            renderChain = Chain(self.renderingProcessing)
            renderChain.process(request=request, response=response, responseCnt=responseCnt, **keyargs)
            if renderChain.doAll().isConsumed():
                if Response.code not in response or response.code.isSuccess:
                    response.code = UNKNOWN_ENCODING
                    response.text = 'Content type \'%s\' not supported for rendering' % responseCnt.type
            else: resolved = True

        if not resolved:
            # Adding None in case some encoder is configured as default.
            for contentType in itertools.chain(request.accTypes or (), self.contentTypeDefaults):
                responseCnt.type = contentType
                renderChain = Chain(self.renderingProcessing)
                renderChain.process(request=request, response=response, responseCnt=responseCnt, **keyargs)
                if not renderChain.doAll().isConsumed(): break
            else:
                raise DevelError('There is no renderer available, this is more likely a setup issues since the '
                                 'default content types should have resolved the renderer')
