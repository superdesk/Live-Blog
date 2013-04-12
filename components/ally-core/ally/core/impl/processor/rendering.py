'''
Created on Jul 12, 2011

@package: ally core
@copyright: 2011 Sourcefabric o.p.s.
@license: http://www.gnu.org/licenses/gpl-3.0.txt
@author: Gabriel Nistor

Provides the rendering processing.
'''

from ally.container.ioc import injected
from ally.core.spec.codes import ENCODING_UNKNOWN
from ally.design.processor.assembly import Assembly
from ally.design.processor.attribute import defines, optional
from ally.design.processor.context import Context
from ally.design.processor.execution import Chain, Processing
from ally.design.processor.handler import HandlerBranchingProceed
from ally.design.processor.processor import Included
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
    code = defines(str)
    isSuccess = defines(bool)
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
class RenderingHandler(HandlerBranchingProceed):
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
        super().__init__(Included(self.renderingAssembly))

    def process(self, rendering, request:Request, response:Response, responseCnt:ResponseContent, **keyargs):
        '''
        @see: HandlerBranchingProceed.process
        
        Create the render for the response object.
        '''
        assert isinstance(rendering, Processing), 'Invalid processing %s' % rendering
        assert isinstance(request, Request), 'Invalid request %s' % request
        assert isinstance(response, Response), 'Invalid response %s' % response
        assert isinstance(responseCnt, ResponseContent), 'Invalid response content %s' % responseCnt
        
        # Resolving the character set
        if responseCnt.charSet:
            try: codecs.lookup(responseCnt.charSet)
            except LookupError: responseCnt.charSet = None
        else: responseCnt.charSet = None

        if not responseCnt.charSet:
            if Request.accCharSets in request and request.accCharSets is not None:
                for charSet in request.accCharSets:
                    try: codecs.lookup(charSet)
                    except LookupError: continue
                    responseCnt.charSet = charSet
                    break
            if not responseCnt.charSet: responseCnt.charSet = self.charSetDefault

        resolved = False
        if responseCnt.type:
            renderChain = Chain(rendering)
            renderChain.process(request=request, response=response, responseCnt=responseCnt, **keyargs)
            if renderChain.doAll().isConsumed():
                if response.isSuccess is not False:
                    response.code, response.isSuccess = ENCODING_UNKNOWN
                    response.text = 'Content type \'%s\' not supported for rendering' % responseCnt.type
            else: resolved = True

        if not resolved:
            # Adding None in case some encoder is configured as default.
            if Request.accTypes in request and request.accTypes is not None:
                contentTypes = itertools.chain(request.accTypes, self.contentTypeDefaults)
            else: contentTypes = self.contentTypeDefaults
            for contentType in contentTypes:
                responseCnt.type = contentType
                renderChain = Chain(rendering)
                renderChain.process(request=request, response=response, responseCnt=responseCnt, **keyargs)
                if not renderChain.doAll().isConsumed(): break
            else:
                raise DevelError('There is no renderer available, this is more likely a setup issues since the '
                                 'default content types should have resolved the renderer')
