'''
Created on Nov 24, 2011

@package: Newscoop
@copyright: 2011 Sourcefabric o.p.s.
@license: http://www.gnu.org/licenses/gpl-3.0.txt
@author: Gabriel Nistor

Provides the configurations for the processors used in handling the request.
'''

from .converter import defaultErrorContentConverter
from .encoder_decoder import handlersDecoding, handlersEncoding
from .parameter import decodersParameters
from .resource_manager import resourcesManager
from ally import ioc
from ally.core.impl.processor.converter import ConverterHandler
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

# --------------------------------------------------------------------
# Creating the processors used in handling the request

@ioc.entity
def handlersExplainError(): return [encoding()]

@ioc.config
def defaultLanguage():
    '''The default language to use in case none is provided in the request'''
    return 'en'

@ioc.config
def explainErrorDetailed():
    '''If True will provide as an error response a detailed XML providing info about where the problem originated'''
    return False
 
@ioc.entity
def explainError() -> ExplainErrorHandler:
    b = ExplainDetailedErrorHandler() if explainErrorDetailed() else ExplainErrorHandler()
    b.encodings = Processors(*handlersExplainError())
    b.languageDefault = defaultLanguage()
    b.contentConverterDefault = defaultErrorContentConverter()
    return b

@ioc.entity
def methodInvoker() -> MethodInvokerHandler: return MethodInvokerHandler()

@ioc.entity
def converter() -> ConverterHandler: return ConverterHandler()

@ioc.entity
def requestTypes() -> RequestTypesHandler: return RequestTypesHandler()

@ioc.entity
def parameters() -> ParametersHandler:
    b = ParametersHandler()
    b.decoders = decodersParameters()
    return b

@ioc.entity
def decoding() -> DecodingHandler:
    b = DecodingHandler()
    b.decodings = Processors(*handlersDecoding())
    return b

@ioc.entity
def invokingHandler() -> InvokingHandler:
    b = InvokingHandler()
    b.resourcesManager = resourcesManager()
    return b

@ioc.entity   
def encoding() -> EncodingProcessorsHandler:
    b = EncodingProcessorsHandler()
    b.encodings = Processors(*handlersEncoding())
    return b
