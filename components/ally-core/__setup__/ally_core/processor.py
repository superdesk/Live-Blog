'''
Created on Nov 24, 2011

@package: ally core
@copyright: 2012 Sourcefabric o.p.s.
@license: http://www.gnu.org/licenses/gpl-3.0.txt
@author: Gabriel Nistor

Provides the configurations for the processors used in handling the request.
'''

from .converter import defaultErrorContentConverter
from .encoder_decoder import handlersDecoding, handlersEncoding
from ally.container import ioc
from ally.core.impl.processor.converter import ConverterHandler
from ally.core.impl.processor.decoding import DecodingHandler
from ally.core.impl.processor.encoding import EncodingProcessorsHandler
from ally.core.impl.processor.explain_error import ExplainErrorHandler, \
    ExplainDetailedErrorHandler
from ally.core.impl.processor.invoking import InvokingHandler
from ally.core.impl.processor.meta_creator import MetaCreatorHandler
from ally.core.impl.processor.method_invoker import MethodInvokerHandler
from ally.core.impl.processor.redirect import RedirectHandler
from ally.core.impl.processor.request_types import RequestTypesHandler
from ally.core.spec.server import Processors, IProcessor

# --------------------------------------------------------------------
# Creating the processors used in handling the request

@ioc.config
def default_language():
    '''The default language to use in case none is provided in the request'''
    return 'en'

@ioc.config
def default_characterset() -> str:
    '''The default character set to use if none is provided in the request'''
    return 'UTF-8'

@ioc.config
def explain_detailed_error():
    '''If True will provide as an error response a detailed response containing info about where the problem originated'''
    return True

@ioc.entity
def explainError() -> IProcessor:
    b = ExplainDetailedErrorHandler() if explain_detailed_error() else ExplainErrorHandler()
    b.encodings = Processors(*handlersExplainError())
    b.languageDefault = default_language()
    b.contentConverterDefault = defaultErrorContentConverter()
    return b

@ioc.entity
def methodInvoker() -> IProcessor: return MethodInvokerHandler()

@ioc.entity
def redirect() -> IProcessor:
    b = RedirectHandler()
    b.redirects = Processors(*handlersRedirect())
    return b

@ioc.entity
def metaCreator() -> IProcessor: return MetaCreatorHandler()

@ioc.entity
def converter() -> IProcessor: return ConverterHandler()

@ioc.entity
def requestTypes() -> IProcessor: return RequestTypesHandler()

@ioc.entity
def decoding() -> IProcessor:
    b = DecodingHandler()
    b.decodings = Processors(*handlersDecoding())
    b.charSetDefault = default_characterset()
    return b

@ioc.entity
def invokingHandler() -> IProcessor: return InvokingHandler()

@ioc.entity
def encoding() -> IProcessor:
    b = EncodingProcessorsHandler()
    b.encodings = Processors(*handlersEncoding())
    b.charSetDefault = default_characterset()
    return b

# ---------------------------------

@ioc.entity
def handlersExplainError():
    '''
    The handlers used for rendering an error message.
    '''
    return [encoding()]

@ioc.entity
def handlersRedirect():
    '''
    The handlers that will be used in processing a redirect.
    '''
    return [converter(), requestTypes(), decoding(), invokingHandler()]

@ioc.entity
def handlersResources():
    '''
    All the handlers that will be used in processing a REST request.
    '''
    return [explainError(), methodInvoker(), redirect(), metaCreator(), converter(), requestTypes(), decoding(),
            invokingHandler(), encoding()]
