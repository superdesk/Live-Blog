'''
Created on Jun 28, 2011

@package: ally core http
@copyright: 2012 Sourcefabric o.p.s.
@license: http://www.gnu.org/licenses/gpl-3.0.txt
@author: Gabriel Nistor

Provides the URI request path handler.
'''

from ally.api.type import Scheme, Type
from ally.container.ioc import injected
from ally.core.spec.resources import ConverterPath, Path, Converter, Normalizer, \
    Node
from ally.design.processor.attribute import requires, defines, optional
from ally.design.processor.context import Context
from ally.design.processor.handler import HandlerProcessorProceed
from ally.http.spec.codes import PATH_FOUND, PATH_NOT_FOUND
from ally.support.core.util_resources import findPath
from urllib.parse import unquote
import logging
from ally.core.impl.node import NodeProperty

# --------------------------------------------------------------------

log = logging.getLogger(__name__)

# --------------------------------------------------------------------

class Request(Context):
    '''
    The request context.
    '''
    # ---------------------------------------------------------------- Required
    uri = requires(str)
    # ---------------------------------------------------------------- Optional
    argumentsOfType = optional(dict)
    # ---------------------------------------------------------------- Defined
    extension = defines(str, doc='''
    @rtype: string
    The extension of the requested URI.
    ''')
    path = defines(Path, doc='''
    @rtype: Path
    The path to the resource node.
    ''')
    converterId = defines(Converter, doc='''
    @rtype: Converter
    The converter to use for model id's.
    ''')
    normalizerParameters = defines(Normalizer, doc='''
    @rtype: Normalizer
    The normalizer to use for decoding parameters names.
    ''')
    converterParameters = defines(Converter, doc='''
    @rtype: Converter
    The converter to use for the parameters values.
    ''')

class Response(Context):
    '''
    The response context.
    '''
    # ---------------------------------------------------------------- Defined
    code = defines(str)
    status = defines(int)
    isSuccess = defines(bool)
    text = defines(str)
    converterId = defines(Converter, doc='''
    @rtype: Converter
    The converter to use for model id's.
    ''')

class ResponseContent(Context):
    '''
    The response content context.
    '''
    # ---------------------------------------------------------------- Defined
    type = defines(str, doc='''
    @rtype: string
    The response content type.
    ''')

# --------------------------------------------------------------------

@injected
class URIHandler(HandlerProcessorProceed):
    '''
    Implementation for a processor that provides the searches based on the request URL the resource path, also
    populates the parameters and extension format on the request.
    '''

    resourcesRoot = Node
    # The resources node that will be used for finding the resource path.
    converterPath = ConverterPath
    # The converter path used for handling the URL path.

    def __init__(self):
        assert isinstance(self.resourcesRoot, Node), 'Invalid resources node %s' % self.resourcesRoot
        assert isinstance(self.converterPath, ConverterPath), 'Invalid ConverterPath object %s' % self.converterPath
        super().__init__()

    def process(self, request:Request, response:Response, responseCnt:ResponseContent, **keyargs):
        '''
        @see: HandlerProcessorProceed.process
        
        Process the URI to a resource path.
        '''
        assert isinstance(request, Request), 'Invalid required request %s' % request
        assert isinstance(response, Response), 'Invalid response %s' % response
        assert isinstance(responseCnt, ResponseContent), 'Invalid response content %s' % responseCnt
        assert isinstance(request.uri, str), 'Invalid request URI %s' % request.uri
        if response.isSuccess is False: return  # Skip in case the response is in error
        
        paths = request.uri.split('/')
        i = paths[-1].rfind('.') if len(paths) > 0 else -1
        if i < 0:
            clearExtension = True
            request.extension = None
        else:
            clearExtension = i == 0
            request.extension = paths[-1][i + 1:].lower()
            paths[-1] = paths[-1][0:i]
        
        paths = [unquote(p) for p in paths if p]

        if request.extension: responseCnt.type = request.extension
        request.path = findPath(self.resourcesRoot, paths, self.converterPath)
        assert isinstance(request.path, Path), 'Invalid path %s' % request.path
        node = request.path.node
        if not node:
            # we stop the chain processing
            response.code, response.status, response.isSuccess = PATH_NOT_FOUND
            assert log.debug('No resource found for URI %s', request.uri) or True
            return
        
        if not clearExtension:
            # We need to check if the last path element is not a string property ant there might be confusion with the extension
            if isinstance(node, NodeProperty):
                assert isinstance(node, NodeProperty)
                assert isinstance(node.type, Type)
                if node.type.isOf(str):
                    response.code, response.status, response.isSuccess = PATH_NOT_FOUND
                    response.text = 'Missing trailing slash'
                    assert log.debug('Unclear extension for URI %s', request.uri) or True
                    return
                
        assert log.debug('Found resource for URI %s', request.uri) or True

        request.converterId = self.converterPath
        request.converterParameters = self.converterPath
        request.normalizerParameters = self.converterPath

        if Request.argumentsOfType in request and request.argumentsOfType is not None:
            request.argumentsOfType[Scheme] = request.scheme

        response.code, response.status, response.isSuccess = PATH_FOUND
        response.converterId = self.converterPath
