'''
Created on Jun 28, 2011

@package: ally core http
@copyright: 2012 Sourcefabric o.p.s.
@license: http://www.gnu.org/licenses/gpl-3.0.txt
@author: Gabriel Nistor

Provides the URI request path handler.
'''

from ally.api.type import Scheme
from ally.container.ioc import injected
from ally.core.http.spec.server import IEncoderPath, IDecoderHeader
from ally.core.spec.codes import RESOURCE_NOT_FOUND, RESOURCE_FOUND, Code
from ally.core.spec.resources import ConverterPath, Path, IResourcesLocator, \
    Converter, Normalizer
from ally.design.processor import Chain, processor, Handler
from urllib.parse import urlencode, urlunsplit, urlsplit
import logging
from ally.design.context import Context, requires, defines, optional

# --------------------------------------------------------------------

log = logging.getLogger(__name__)

# --------------------------------------------------------------------

class Request(Context):
    '''
    The request context.
    '''
    # ---------------------------------------------------------------- Required
    scheme = requires(str)
    uriRoot = requires(str)
    uri = requires(str)
    decoderHeader = requires(IDecoderHeader)
    # ---------------------------------------------------------------- Optional
    argumentsOfType = optional(dict)
    # ---------------------------------------------------------------- Defined
    path = defines(Path, doc='''
    @rtype: Path
    The path to the resource node.
    ''')
    normalizer = defines(Normalizer, doc='''
    @rtype: Normalizer
    The normalizer to use for decoding parameters names.
    ''')
    converter = defines(Converter, doc='''
    @rtype: Converter
    The converter to use for the parameters values.
    ''')

class Response(Context):
    '''
    The response context.
    '''
    # ---------------------------------------------------------------- Defined
    code = defines(Code)
    text = defines(str)
    encoderPath = defines(IEncoderPath)

class ResponseContent(Context):
    '''
    The response content context.
    '''
    type = defines(str)
    converterId = defines(Converter)

# --------------------------------------------------------------------

@injected
class URIHandler(Handler):
    '''
    Implementation for a processor that provides the searches based on the request URL the resource path, also
    populates the parameters and extension format on the request.
    '''

    resourcesLocator = IResourcesLocator
    # The resources locator that will provide the path to the resource node.
    converterPath = ConverterPath
    # The converter path used for handling the URL path.
    headerHost = 'Host'
    # The header in which the host is provided.

    def __init__(self):
        assert isinstance(self.resourcesLocator, IResourcesLocator), \
        'Invalid resources locator %s' % self.resourcesLocator
        assert isinstance(self.converterPath, ConverterPath), 'Invalid ConverterPath object %s' % self.converterPath
        assert isinstance(self.headerHost, str), 'Invalid string %s' % self.headerHost

    @processor
    def process(self, chain, request:Request, response:Response, responseCnt:ResponseContent, **keyargs):
        '''
        Process the URI to a resource path.
        '''
        assert isinstance(chain, Chain), 'Invalid processors chain %s' % chain
        assert isinstance(request, Request), 'Invalid required request %s' % request
        assert isinstance(response, Response), 'Invalid response %s' % response
        assert isinstance(responseCnt, ResponseContent), 'Invalid response content %s' % responseCnt
        assert isinstance(request.uri, str), 'Invalid request URI %s' % request.uri

        paths = request.uri.split('/')
        i = paths[-1].rfind('.') if len(paths) > 0 else -1
        if i < 0:
            extension = None
        else:
            extension = paths[-1][i + 1:].lower()
            paths[-1] = paths[-1][0:i]
        paths = [p for p in paths if p]

        request.path = self.resourcesLocator.findPath(self.converterPath, paths)
        assert isinstance(request.path, Path), 'Invalid path %s' % request.path
        if not request.path.node:
            # we stop the chain processing
            response.code, response.text = RESOURCE_NOT_FOUND, 'Cannot find resources for path'
            assert log.debug('No resource found for URI %s', request.uri) or True
            return
        assert log.debug('Found resource for URL %s', request.uri) or True

        request.converter = self.converterPath
        request.normalizer = self.converterPath

        if Request.argumentsOfType in request: request.argumentsOfType[Scheme] = request.scheme

        response.code = RESOURCE_FOUND
        response.encoderPath = self.createEncoderPath(request, extension)
        responseCnt.converterId = self.converterPath
        if extension: responseCnt.type = extension

        chain.proceed()

    # ----------------------------------------------------------------

    def createEncoderPath(self, request, extension=None):
        '''
        Creates the path encoder for the provided request.
        
        @param request: Request
            The request to create the path encoder for.
        @param extension: string
            The extension to use on the encoded paths.
        '''
        assert isinstance(request, Request), 'Invalid request %s' % request
        assert isinstance(request.decoderHeader, IDecoderHeader), \
        'Invalid request decoder header %s' % request.decoderHeader
        assert isinstance(request.uriRoot, str), 'Invalid request root URI %s' % request.uriRoot
        assert extension is None or isinstance(extension, str), 'Invalid extension %s' % extension

        host = request.decoderHeader.retrieve(self.headerHost)
        return EncoderPathURI(request.scheme, host, request.uriRoot, self.converterPath, extension)

# --------------------------------------------------------------------

class EncoderPathURI(IEncoderPath):
    '''
    Provides encoding for the URI paths generated by the URI processor.
    '''

    __slots__ = ('scheme', 'host', 'root', 'converterPath', 'extension')

    def __init__(self, scheme, host, root, converterPath, extension):
        '''
        @param scheme: string
            The encoded path scheme.
        @param host: string
            The host string.
        @param root: string
            The root URI to be considered for constructing a request path, basically the relative path root. None if the path
            is not relative.
        @param converterPath: ConverterPath
            The converter path to be used on Path objects to get the URL.
        @param extension: string
            The extension to use on the encoded paths.
        '''
        assert isinstance(scheme, str), 'Invalid scheme %s' % scheme
        assert isinstance(host, str), 'Invalid host %s' % host
        assert isinstance(root, str), 'Invalid root URI %s' % root
        assert isinstance(converterPath, ConverterPath), 'Invalid converter path %s' % converterPath
        assert extension is None or isinstance(extension, str), 'Invalid extension %s' % extension
        self.scheme = scheme
        self.host = host
        self.root = root
        self.converterPath = converterPath
        self.extension = extension

    def encode(self, path, parameters=None):
        '''
        @see: EncoderPath.encode
        '''
        assert isinstance(path, (Path, str)), 'Invalid path %s' % path
        if isinstance(path, Path):
            assert isinstance(path, Path)
            paths = path.toPaths(self.converterPath)
            if self.extension: paths.append('.' + self.extension)
            elif path.node.isGroup: paths.append('')

            query = urlencode(parameters) if parameters else ''
            return urlunsplit((self.scheme, self.host, self.root + '/'.join(paths), query, ''))
        else:
            assert isinstance(path, str), 'Invalid path %s' % path
            if not path.strip().startswith('/'):
                #TODO: improve the relative path detection
                # This is an absolute path so we will return it as it is.
                return path
            # The path is relative to this server so we will convert it in an absolute path
            url = urlsplit(path)
            return urlunsplit((self.scheme, self.host, url.path, url.query, url.fragment))
