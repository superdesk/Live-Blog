'''
Created on Jan 31, 2013

@package: ally http
@copyright: 2012 Sourcefabric o.p.s.
@license: http://www.gnu.org/licenses/gpl-3.0.txt
@author: Gabriel Nistor

Provides the path encoder.
'''

from ally.container.ioc import injected
from ally.design.processor.attribute import requires, defines
from ally.design.processor.context import Context
from ally.design.processor.handler import HandlerProcessorProceed
from ally.http.spec.server import IDecoderHeader, IEncoderPath
from ally.support.util import Singletone
from collections import Iterable
from urllib.parse import urlsplit, urlunsplit, urlencode
import logging

# --------------------------------------------------------------------

log = logging.getLogger(__name__)

# --------------------------------------------------------------------

class Request(Context):
    '''
    The request context.
    '''
    # ---------------------------------------------------------------- Required
    scheme = requires(str)
    decoderHeader = requires(IDecoderHeader)

class Response(Context):
    '''
    The response context.
    '''
    # ---------------------------------------------------------------- Defined
    code = defines(str)
    status = defines(int)
    isSuccess = defines(bool)
    encoderPath = defines(IEncoderPath, doc='''
    @rtype: IEncoderPath
    The path encoder used for encoding paths that will be rendered in the response.
    ''')
    
# --------------------------------------------------------------------

@injected
class EncoderPathHandler(HandlerProcessorProceed):
    '''
    Provides the path encoder for the response.
    '''

    headerHost = 'Host'
    # The header in which the host is provided.

    def __init__(self):
        assert isinstance(self.headerHost, str), 'Invalid string %s' % self.headerHost
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

        host = request.decoderHeader.retrieve(self.headerHost)
        if host is None:
            response.encoderPath = EncoderPathNothing()
            assert log.debug('No host header available for URI %s', request.uri) or True
            return
        response.encoderPath = EncoderPathHost(request.scheme, host)

# --------------------------------------------------------------------

class EncoderPathNothing(Singletone, IEncoderPath):
    '''
    Provides no encoding for URIs.
    '''
    __slots__ = ()

    def encode(self, path, parameters=None):
        '''
        @see: IEncoderPath.encode
        '''
        assert isinstance(path, str), 'Invalid path %s' % path
        url = urlsplit(path)
        assert not url.query, 'No query expected for path \'%s\'' % path
        assert not url.fragment, 'No fragment expected for path \'%s\'' % path
        if parameters:
            assert isinstance(parameters, Iterable), 'Invalid parameters %s' % parameters
            if not isinstance(parameters, list): parameters = list(parameters)
            for name, value in parameters:
                assert isinstance(name, str), 'Invalid parameter name %s' % name
                assert isinstance(value, str), 'Invalid parameter value %s' % value
            parameters = urlencode(parameters)
        else: parameters = ''
        return urlunsplit((url.scheme, url.netloc, url.path, parameters, ''))
    
    def encodePattern(self, path):
        '''
        @see: IEncoderPath.encodePattern
        '''
        raise NotImplementedError('Not need to implement, at least until now')

class EncoderPathHost(IEncoderPath):
    '''
    Provides encoding host prefixing for the URI paths to be encoded in the response.
    '''

    __slots__ = ('_scheme', '_host')

    def __init__(self, scheme, host):
        '''
        Construct the encoder.
        
        @param scheme: string
            The encoded path scheme.
        @param host: string
            The host string.
        '''
        assert isinstance(scheme, str), 'Invalid scheme %s' % scheme
        assert isinstance(host, str), 'Invalid host %s' % host
        self._scheme = scheme
        self._host = host

    def encode(self, path, parameters=None):
        '''
        @see: IEncoderPath.encode
        
        @param parameters: Iterable(tuple(string, string))
            A iterable of tuples containing on the first position the parameter string name and on the second the string
            parameter value as to be represented in the request path.
        '''
        assert isinstance(path, str), 'Invalid path %s' % path
        url = urlsplit(path)
        assert not url.query, 'No query expected for path \'%s\'' % path
        assert not url.fragment, 'No fragment expected for path \'%s\'' % path
        if parameters:
            assert isinstance(parameters, Iterable), 'Invalid parameters %s' % parameters
            if not isinstance(parameters, list): parameters = list(parameters)
            for name, value in parameters:
                assert isinstance(name, str), 'Invalid parameter name %s' % name
                assert isinstance(value, str), 'Invalid parameter value %s' % value
            parameters = urlencode(parameters)
        else: parameters = ''
        if url.scheme: return urlunsplit((url.scheme, url.netloc, url.path, parameters, ''))
        if url.netloc: return urlunsplit((self._scheme, url.netloc, url.path, parameters, ''))
        # We just needed to append the scheme
        return urlunsplit((self._scheme, self._host, url.path, parameters, ''))
    
    def encodePattern(self, path):
        '''
        @see: IEncoderPath.encodePattern
        '''
        raise NotImplementedError('Not need to implement, at least until now')
