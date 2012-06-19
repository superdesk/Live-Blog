'''
Created on Nov 24, 2011

@package: ally core http
@copyright: 2011 Sourcefabric o.p.s.
@license: http://www.gnu.org/licenses/gpl-3.0.txt
@author: Gabriel Nistor

Provides the configurations for the processors used in handling the request.
'''

from . import server_pattern_rest
from ..ally_core.processor import argumentsOfType, encoding, resourcesAssembly, \
    methodInvoker
from ..ally_core.resources import resourcesLocator
from .meta_service import parameterMetaService
from ally.container import ioc
from ally.core.http.impl.processor.header import HeaderHandler
from ally.core.http.impl.processor.headers.accept import AcceptDecodeHandler
from ally.core.http.impl.processor.headers.allow import AllowEncodeHandler
from ally.core.http.impl.processor.headers.content_disposition import \
    ContentDispositionDecodeHandler
from ally.core.http.impl.processor.headers.content_language import \
    ContentLanguageDecodeHandler, ContentLanguageEncodeHandler
from ally.core.http.impl.processor.headers.content_length import \
    ContentLengthDecodeHandler, ContentLengthEncodeHandler
from ally.core.http.impl.processor.headers.content_type import \
    ContentTypeDecodeHandler, ContentTypeEncodeHandler
from ally.core.http.impl.processor.headers.override_method import \
    MethodOverrideDecodeHandler
from ally.core.http.impl.processor.parameter import ParameterHandler
from ally.core.http.impl.processor.uri import URIHandler
from ally.core.spec.resources import ConverterPath
from ally.design.processor import Handler

# --------------------------------------------------------------------
# Creating the processors used in handling the request

@ioc.config
def read_from_params():
    '''If true will also read header values that are provided as query parameters'''
    return True

@ioc.config
def allow_method_override():
    '''
    If true will allow the method override by using the header 'X-HTTP-Method-Override', the GET can be override with
    DELETE and the POST with PUT.
    '''
    return True

# --------------------------------------------------------------------

@ioc.entity
def converterPath() -> ConverterPath: return ConverterPath()

@ioc.entity
def header() -> Handler:
    b = HeaderHandler()
    b.useParameters = read_from_params()
    return b

# --------------------------------------------------------------------
# Header decoders

@ioc.entity
def contentTypeDecode() -> Handler: return ContentTypeDecodeHandler()

@ioc.entity
def contentDispositionDecode() -> Handler: return ContentDispositionDecodeHandler()

@ioc.entity
def contentLengthDecode() -> Handler: return ContentLengthDecodeHandler()

@ioc.entity
def contentLanguageDecode() -> Handler: return ContentLanguageDecodeHandler()

@ioc.entity
def acceptDecode() -> Handler: return AcceptDecodeHandler()

@ioc.entity
def methodOverrideDecode() -> Handler: return MethodOverrideDecodeHandler()

# --------------------------------------------------------------------
# Header encoders

@ioc.entity
def contentTypeEncode() -> Handler: return ContentTypeEncodeHandler()

@ioc.entity
def contentLengthEncode() -> Handler: return ContentLengthEncodeHandler()

@ioc.entity
def contentLanguageEncode() -> Handler: return ContentLanguageEncodeHandler()

@ioc.entity
def allowEncode() -> Handler: return AllowEncodeHandler()

# --------------------------------------------------------------------

@ioc.entity
def uri() -> Handler:
    b = URIHandler()
    b.resourcesLocator = resourcesLocator()
    b.converterPath = converterPath()
    return b

@ioc.entity
def parameter() -> Handler:
    b = ParameterHandler()
    b.parameterMetaService = parameterMetaService()
    return b

@ioc.entity
def pathHandlers():
    return [(server_pattern_rest(), resourcesAssembly())]

# --------------------------------------------------------------------

@ioc.before(resourcesAssembly)
def updateResourcesAssembly():
    resourcesAssembly().add(header(), uri(), contentTypeDecode(), contentLengthDecode(), contentLanguageDecode(),
                            contentDispositionDecode(), acceptDecode(), after=argumentsOfType())

    resourcesAssembly().add(parameter(), after=methodInvoker())

    resourcesAssembly().add(contentTypeEncode(), contentLanguageEncode(), allowEncode(), after=encoding())

    if allow_method_override():
        resourcesAssembly().add(methodOverrideDecode(), before=uri())
