'''
Created on Jun 1, 2012

@package: ally core http
@copyright: 2012 Sourcefabric o.p.s.
@license: http://www.gnu.org/licenses/gpl-3.0.txt
@author: Gabriel Nistor

Provides HTTP server specification.
'''

from ally.support.util_io import IInputStream, IOutputStream
from ally.core.spec.codes import Code
from ally.design.context import Context, defines, requires, optional
from collections import Iterable
import abc

# --------------------------------------------------------------------
# Additional HTTP methods.

METHOD_OPTIONS = 16

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
    method = defines(int, doc='''
    @rtype: integer
    The method of the request.
    ''')
    uriRoot = defines(str, doc='''
    @rtype: string
    The root URI to be considered for constructing a request path, basically the relative path root.
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
    code = requires(Code, doc='''
    @rtype: Code
    The response code.
    ''')
    # ---------------------------------------------------------------- Optional
    text = optional(str, doc='''
    @rtype: str
    The response text message (a short message).
    ''')
    headers = optional(dict, doc='''
    @rtype: dictionary{String, string}
    The response headers.
    ''')

class ResponseContentHTTP(Context):
    '''
    Context for HTTP response content data. 
    '''
    # ---------------------------------------------------------------- Required
    source = requires(IOutputStream, Iterable, doc='''
    @rtype: IOutputStream|Iterable
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

class IEncoderPath(metaclass=abc.ABCMeta):
    '''
    Provides the path encoding.
    '''

    @abc.abstractmethod
    def encode(self, path, parameters=None):
        '''
        Encodes the provided path to a full request path.
        
        @param path: Path|string
            The path to be encoded, for a local REST resource it will be a Path object, also it can be a string that will
            be interpreted as a path.
        @param parameters: list
            A list of tuples containing on the first position the parameter string name and on the second the string
            parameter value as to be represented in the request path.
        @return: object
            The full compiled request path, the type depends on the implementation.
        '''
