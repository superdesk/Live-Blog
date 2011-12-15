'''
Created on Nov 24, 2011

@package: Newscoop
@copyright: 2011 Sourcefabric o.p.s.
@license: http://www.gnu.org/licenses/gpl-3.0.txt
@author: Gabriel Nistor

Provides the configurations for the processors used in handling the request.
'''

from ally.core.impl.processor.converter import ConverterHandler
from ally.core.impl.processor.decoding import DecodingHandler
from ally.core.impl.processor.encoding import EncodingProcessorsHandler
from ally.core.impl.processor.explain_error import ExplainErrorHandler
from ally.core.impl.processor.invoking import InvokingHandler
from ally.core.impl.processor.method_invoker import MethodInvokerHandler
from ally.core.impl.processor.parameters import ParametersHandler
from ally.core.impl.processor.request_types import RequestTypesHandler
from ally.core.spec.server import Processors
from ally.http.processor.header import HeaderStandardHandler
from ally.http.processor.header_x import HeaderXHandler
from ally.http.processor.uri import URIHandler

# --------------------------------------------------------------------
# Creating the processors used in handling the request

def explainError(headerStandard, encoding, defaultErrorContentConverter, _defaultLanguage) -> ExplainErrorHandler:
    b = ExplainErrorHandler()
    b.encodings = Processors(headerStandard, encoding)
    b.languageDefault = _defaultLanguage
    b.contentConverterDefault = defaultErrorContentConverter
    return b
    
def uri(resourcesManager, converterPath, _serverRoot) -> URIHandler:
    b = URIHandler()
    b.resourcesManager = resourcesManager
    b.converterPath = converterPath
    if _serverRoot: b.urlRoot = _serverRoot + '/'
    return b
    
def headerStandard(_readFromParams=True) -> HeaderStandardHandler:
    b = HeaderStandardHandler()
    b.readFromParams = _readFromParams
    return b

def methodInvoker() -> MethodInvokerHandler: return MethodInvokerHandler()

def headerX(contentNormalizer, _readFromParams) -> HeaderXHandler:
    b = HeaderXHandler()
    b.normalizer = contentNormalizer
    b.readFromParams = _readFromParams
    return b

def converter(_defaultLanguage:'The default language to use in case none is provided in the '
              'request'='en') -> ConverterHandler:
    b = ConverterHandler()
    b.languageDefault = _defaultLanguage
    return b

def requestTypes() -> RequestTypesHandler: return RequestTypesHandler()

def parameters(decodersParameters) -> ParametersHandler:
    b = ParametersHandler()
    b.decoders = decodersParameters
    return b

def decoding(handlersDecoding) -> DecodingHandler:
    b = DecodingHandler()
    b.decodings = Processors(*handlersDecoding)
    return b

def invokingHandler(resourcesManager) -> InvokingHandler:
    b = InvokingHandler()
    b.resourcesManager = resourcesManager
    return b
    
def encoding(handlersEncoding) -> EncodingProcessorsHandler:
    b = EncodingProcessorsHandler()
    b.encodings = Processors(*handlersEncoding)
    return b

# ---------------------------------

handlers = lambda ctx: [ctx.explainError, ctx.uri, ctx.headerStandard, ctx.methodInvoker, ctx.headerX, ctx.converter,
                        ctx.requestTypes, ctx.parameters, ctx.decoding, ctx.invokingHandler, ctx.encoding]
