'''
Created on Nov 24, 2011

@package: ally core
@copyright: 2012 Sourcefabric o.p.s.
@license: http://www.gnu.org/licenses/gpl-3.0.txt
@author: Gabriel Nistor

Provides the configurations for the processors used in handling the request.
'''

from .encoder_decoder import renderingAssembly, parsingAssembly
from ally.container import ioc
from ally.core.impl.processor.arguments import ArgumentsPrepareHandler, \
    ArgumentsBuildHandler
from ally.core.impl.processor.content import ContentHandler
from ally.core.impl.processor.decoder import CreateDecoderHandler
from ally.core.impl.processor.encoder import CreateEncoderHandler
from ally.core.impl.processor.explain_error import ExplainErrorHandler
from ally.core.impl.processor.invoking import InvokingHandler
from ally.core.impl.processor.method_invoker import MethodInvokerHandler
from ally.core.impl.processor.parsing import ParsingHandler
from ally.core.impl.processor.render_encoder import RenderEncoderHandler
from ally.core.impl.processor.rendering import RenderingHandler
from ally.core.impl.processor.text_conversion import ConversionSetHandler
from ally.core.spec.resources import Normalizer, Converter
from ally.design.processor import Handler, Assembly

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

@ioc.config
def allow_chuncked_response():
    '''Flag indicating that a chuncked transfer is allowed, more or less if this is false a length is a must'''
    return False

@ioc.config
def chunck_size():
    '''The buffer size used in the generator returned chuncks'''
    return 4096

# --------------------------------------------------------------------

@ioc.entity
def normalizer() -> Normalizer: return Normalizer()

@ioc.entity
def converter() -> Converter: return Converter()

# --------------------------------------------------------------------

@ioc.entity
def argumentsPrepare() -> Handler: return ArgumentsPrepareHandler()

@ioc.entity
def methodInvoker() -> Handler: return MethodInvokerHandler()

@ioc.entity
def renderer() -> Handler:
    b = RenderingHandler()
    b.charSetDefault = default_characterset()
    b.renderingAssembly = renderingAssembly()
    return b

@ioc.entity
def conversion() -> Handler:
    b = ConversionSetHandler()
    b.normalizer = normalizer()
    b.converter = converter()
    return b

@ioc.entity
def createDecoder() -> Handler: return CreateDecoderHandler()

@ioc.entity
def createEncoder() -> Handler: return CreateEncoderHandler()

@ioc.entity
def parser() -> Handler:
    b = ParsingHandler()
    b.charSetDefault = default_characterset()
    b.parsingAssembly = parsingAssembly()
    return b

@ioc.entity
def content() -> Handler: return ContentHandler()

@ioc.entity
def argumentsBuild() -> Handler: return ArgumentsBuildHandler()

@ioc.entity
def invoking() -> Handler: return InvokingHandler()

@ioc.entity
def renderEncoder() -> Handler:
    b = RenderEncoderHandler()
    b.allowChunked = allow_chuncked_response()
    b.bufferSize = chunck_size()
    return b

@ioc.entity
def explainError(): return ExplainErrorHandler()

# --------------------------------------------------------------------

@ioc.entity
def assemblyResources() -> Assembly:
    '''
    The assembly containing the handlers that will be used in processing a REST request.
    '''
    return Assembly()

# --------------------------------------------------------------------

@ioc.before(assemblyResources)
def updateAssemblyResources():
    assemblyResources().add(argumentsPrepare(), methodInvoker(), renderer(), conversion(), createDecoder(),
                            createEncoder(), parser(), content(), argumentsBuild(), invoking(), renderEncoder(),
                            explainError())
