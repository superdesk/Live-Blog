'''
Created on Nov 24, 2011

@package: ally core http
@copyright: 2011 Sourcefabric o.p.s.
@license: http://www.gnu.org/licenses/gpl-3.0.txt
@author: Gabriel Nistor

Provides the configurations for the processors used in handling the request.
'''

from ..ally_core.encoder_decoder import assemblyParsing
from ..ally_core.processor import argumentsBuild, argumentsPrepare, \
    renderEncoder, invoking, default_characterset, renderer, conversion, \
    createDecoder, content
from ..ally_core.resources import resourcesRoot
from ..ally_http.processor import encoderPath, contentLengthDecode, \
    contentLengthEncode, methodOverride, allowEncode, headerDecodeRequest, \
    contentTypeRequestDecode, headerEncodeResponse, contentTypeResponseEncode
from ally.container import ioc
from ally.core.http.impl.processor.encoder import CreateEncoderWithPathHandler
from ally.core.http.impl.processor.explain_error import ExplainErrorHandler
from ally.core.http.impl.processor.fetcher import FetcherHandler
from ally.core.http.impl.processor.headers.accept import AcceptDecodeHandler
from ally.core.http.impl.processor.headers.content_disposition import \
    ContentDispositionDecodeHandler
from ally.core.http.impl.processor.headers.content_language import \
    ContentLanguageDecodeHandler, ContentLanguageEncodeHandler
from ally.core.http.impl.processor.internal_error import \
    InternalDevelErrorHandler
from ally.core.http.impl.processor.method_invoker import MethodInvokerHandler
from ally.core.http.impl.processor.parameter import ParameterHandler
from ally.core.http.impl.processor.parsing_multipart import \
    ParsingMultiPartHandler
from ally.core.http.impl.processor.redirect import RedirectHandler
from ally.core.http.impl.processor.uri import URIHandler
from ally.core.http.spec.codes import CODE_TO_STATUS, CODE_TO_TEXT
from ally.core.spec.resources import ConverterPath
from ally.design.processor.assembly import Assembly
from ally.design.processor.handler import Handler
from ally.http.impl.processor.status import StatusHandler
from ally.core.http.impl.processor.path_encoder_resource import ResourcePathEncoderHandler

# --------------------------------------------------------------------
# Creating the processors used in handling the request

@ioc.config
def allow_method_override():
    '''
    If true will allow the method override by using the header 'X-HTTP-Method-Override', the GET can be override with
    DELETE and the POST with PUT.
    '''
    return True

@ioc.config
def root_uri_resources():
    '''
    This will be used for adjusting the encoded URIs to have a root URI.
    !Attention this configuration needs to be in concordance with 'server_pattern_resources' configuration
    '''
    return 'resources/%s'

# --------------------------------------------------------------------

@ioc.entity
def converterPath() -> ConverterPath: return ConverterPath()

# --------------------------------------------------------------------
# Header decoders

@ioc.entity
def internalDevelError() -> Handler: return InternalDevelErrorHandler()

@ioc.entity
def contentDispositionDecode() -> Handler: return ContentDispositionDecodeHandler()

@ioc.entity
def contentLanguageDecode() -> Handler: return ContentLanguageDecodeHandler()

@ioc.entity
def acceptDecode() -> Handler: return AcceptDecodeHandler()

@ioc.entity
def methodInvoker() -> Handler: return MethodInvokerHandler()

# --------------------------------------------------------------------
# Header encoders

@ioc.entity
def contentLanguageEncode() -> Handler: return ContentLanguageEncodeHandler()

# --------------------------------------------------------------------

@ioc.entity
def uri() -> Handler:
    b = URIHandler()
    b.resourcesRoot = resourcesRoot()
    b.converterPath = converterPath()
    return b

@ioc.entity
def encoderPathResource() -> Handler:
    b = ResourcePathEncoderHandler()
    b.resourcesRootURI = root_uri_resources()
    b.converterPath = converterPath()
    return b

@ioc.entity
def parameter() -> Handler: return ParameterHandler()

@ioc.entity
def fetcher() -> Handler: return FetcherHandler()

@ioc.entity
def createEncoderWithPath() -> Handler: return CreateEncoderWithPathHandler()

@ioc.entity
def parserMultiPart() -> Handler:
    b = ParsingMultiPartHandler()
    b.charSetDefault = default_characterset()
    b.parsingAssembly = assemblyParsing()
    b.populateAssembly = assemblyMultiPartPopulate()
    return b

@ioc.entity
def redirect() -> Handler:
    b = RedirectHandler()
    b.redirectAssembly = assemblyRedirect()
    return b

@ioc.entity
def statusCodeToStatus(): return dict(CODE_TO_STATUS)

@ioc.entity
def statusCodeToText(): return dict(CODE_TO_TEXT)

@ioc.entity
def status() -> Handler:
    b = StatusHandler()
    b.codeToStatus = statusCodeToStatus()
    b.codeToText = statusCodeToText()
    return b

@ioc.entity
def explainError(): return ExplainErrorHandler()

# --------------------------------------------------------------------

@ioc.entity
def assemblyResources() -> Assembly:
    '''
    The assembly containing the handlers that will be used in processing a REST request.
    '''
    return Assembly('REST resources')

@ioc.entity
def assemblyMultiPartPopulate() -> Assembly:
    '''
    The assembly containing the handlers that will populate data on the next request content.
    '''
    return Assembly('Multipart content')

@ioc.entity
def assemblyRedirect() -> Assembly:
    '''
    The assembly containing the handlers that will be used in processing a redirect.
    '''
    return Assembly('Redirect')

# --------------------------------------------------------------------

@ioc.before(assemblyResources)
def updateAssemblyResources():
    assemblyResources().add(internalDevelError(), headerDecodeRequest(), encoderPath(),
                            argumentsPrepare(), uri(), encoderPathResource(), methodInvoker(), headerEncodeResponse(), redirect(),
                            contentTypeRequestDecode(), contentLengthDecode(), contentLanguageDecode(), acceptDecode(),
                            renderer(), conversion(), createDecoder(), createEncoderWithPath(), parserMultiPart(), content(),
                            parameter(), fetcher(), argumentsBuild(), invoking(), renderEncoder(),
                            status(), explainError(), contentTypeResponseEncode(),
                            contentLanguageEncode(), contentLengthEncode(), allowEncode())
    
    if allow_method_override(): assemblyResources().add(methodOverride(), before=methodInvoker())

@ioc.before(assemblyMultiPartPopulate)
def updateAssemblyMultiPartPopulate():
    assemblyMultiPartPopulate().add(headerDecodeRequest(), contentTypeRequestDecode(), contentDispositionDecode())

@ioc.before(assemblyRedirect)
def updateAssemblyRedirect():
    assemblyRedirect().add(argumentsBuild(), invoking())
