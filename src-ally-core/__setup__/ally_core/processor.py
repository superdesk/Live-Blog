'''
Created on Nov 24, 2011

@package: Newscoop
@copyright: 2011 Sourcefabric o.p.s.
@license: http://www.gnu.org/licenses/gpl-3.0.txt
@author: Gabriel Nistor

Provides the configurations for the processors used in handling the request.
'''

from ally.core.impl.processor.decoding import DecodingHandler
from ally.core.impl.processor.encoding import EncodingProcessorsHandler
from ally.core.impl.processor.explain_detailed_error import \
    ExplainDetailedErrorHandler
from ally.core.impl.processor.explain_error import ExplainErrorHandler
from ally.core.impl.processor.invoking import InvokingHandler
from ally.core.impl.processor.method_invoker import MethodInvokerHandler
from ally.core.impl.processor.parameters import ParametersHandler
from ally.core.impl.processor.request_types import RequestTypesHandler
from ally.core.spec.server import Processors
from ally.core.impl.processor.converter import ConverterHandler

# --------------------------------------------------------------------
# Creating the processors used in handling the request

handlersExplainError = lambda ctx: [ctx.encoding]

def explainError(handlersExplainError, defaultErrorContentConverter,
                 _defaultLanguage:'The default language to use in case none is provided in the request'='en',
                 _detailed:'If true will provide as an error response a detailed XML providing info about where the '
                 'problem originated'=False) -> ExplainErrorHandler:
    b = ExplainDetailedErrorHandler() if _detailed else ExplainErrorHandler()
    b.encodings = Processors(*handlersExplainError)
    b.languageDefault = _defaultLanguage
    b.contentConverterDefault = defaultErrorContentConverter
    return b

def methodInvoker() -> MethodInvokerHandler: return MethodInvokerHandler()

def converter() -> ConverterHandler: return ConverterHandler()

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
