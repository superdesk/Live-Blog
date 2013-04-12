'''
Created on Jun 1, 2012

@package: ally http
@copyright: 2012 Sourcefabric o.p.s.
@license: http://www.gnu.org/licenses/gpl-3.0.txt
@author: Gabriel Nistor

Provides HTTP server specification.
'''

from ally.design.processor.attribute import requires, optional, defines
from ally.design.processor.context import Context
from ally.support.util_io import IInputStream
from collections import Iterable
import abc

# --------------------------------------------------------------------

# HTTP scheme/protocol.
HTTP = 'http'

# HTTP methods.
HTTP_GET = 'GET'
HTTP_DELETE = 'DELETE'
HTTP_POST = 'POST'
HTTP_PUT = 'PUT'
HTTP_OPTIONS = 'OPTIONS'

# --------------------------------------------------------------------

class RequestHTTP(Context):
    '''
    Context for HTTP request data. 
    '''
    # ---------------------------------------------------------------- Defined
    scheme = defines(str, doc='''
    @rtype: string
    The scheme URI protocol name to be used for the response.
    ''')
    method = defines(str, doc='''
    @rtype: string
    The method name of the request.
    ''')
    uri = defines(str, doc='''
    @rtype: string
    The relative request URI.
    ''')
    parameters = defines(list, doc='''
    @rtype: list[tuple(string, string)]
    The parameters of the request.
    ''')
    headers = defines(dict, doc='''
    @rtype: dictionary{string, string}
    The raw headers.
    ''')

class RequestContentHTTP(Context):
    '''
    Context for HTTP request content data. 
    '''
    # ---------------------------------------------------------------- Defined
    source = defines(IInputStream, doc='''
    @rtype: IInputStream
    The source for the request content.
    ''')

class ResponseHTTP(Context):
    '''
    Context for HTTP response data. 
    '''
    # ---------------------------------------------------------------- Required
    status = requires(int, doc='''
    @rtype: integer
    The response status code.
    ''')
    # ---------------------------------------------------------------- Optional
    code = optional(str, doc='''
    @rtype: string
    The response code message.
    ''')
    text = optional(str, doc='''
    @rtype: string
    The response text message (a short message).
    ''')
    headers = optional(dict, doc='''
    @rtype: dictionary{string, string}
    The response headers.
    ''')

class ResponseContentHTTP(Context):
    '''
    Context for HTTP response content data. 
    '''
    # ---------------------------------------------------------------- Required
    source = optional(IInputStream, Iterable, doc='''
    @rtype: IInputStream|Iterable
    The source for the response content.
    ''')

# --------------------------------------------------------------------

class IDecoderHeader(metaclass=abc.ABCMeta):
    '''
    Provides the header retrieve, parsing and decoding.
    '''

    @abc.abstractmethod
    def retrieve(self, name):
        '''
        Get the raw header value.
        
        @param name: string
            The name of the header to retrieve.
        @return: string|None
            The raw header value or None if there is no such header.
        '''

    @abc.abstractmethod
    def decode(self, name):
        '''
        Get the decoded the header value.
        
        @param name: string
            The name of the header to decode.
        @return: list[tuple(string, dictionary{string:string})]
            A list of tuples having as the first entry the header value and the second entry a dictionary 
            with the value attribute.
        '''

class IEncoderHeader(metaclass=abc.ABCMeta):
    '''
    Provides the header encoding.
    '''

    @abc.abstractmethod
    def encode(self, name, *value):
        '''
        Encodes the header values.
        ex:
            convert('multipart/formdata', 'mixed') == 'multipart/formdata, mixed'
            
            convert(('multipart/formdata', ('charset', 'utf-8'), ('boundry', '12))) ==
            'multipart/formdata; charset=utf-8; boundry=12'
        
        @param name: string
            The name of the header to set.
        @param value: arguments[tuple(string, tuple(string, string))|string]
            Tuples containing as first value found in the header and as the second value a tuple with the
            values attribute.
        '''
        
# --------------------------------------------------------------------

class IEncoderPath(metaclass=abc.ABCMeta):
    '''
    Provides the path encoding.
    '''

    @abc.abstractmethod
    def encode(self, path, **keyargs):
        '''
        Encodes the provided path to a full request path.
        
        @param path: object
            The path to be encoded, the type depends on the implementation.
        @param keyargs: key arguments
            Key arguments containing specific data that can be handled by the encoder, if unknown or invalid data is provided 
            then the encoder has the duty to report that.
        @return: string
            The full compiled request path.
        '''
        
    @abc.abstractmethod
    def encodePattern(self, path, **keyargs):
        '''
        Encodes the provided path to a pattern path that can be used as regex to identify paths corresponding to the provided
        path.
        
        @param path: object
            The path to be encoded as a pattern, the type depends on the implementation.
        @param keyargs: key arguments
            Key arguments containing specific data that can be handled by the encoder, if unknown or invalid data is provided 
            then the encoder has the duty to report that.
        @return: string
            The path pattern.
        '''
