'''
Created on Nov 24, 2011

@package: ally core
@copyright: 2012 Sourcefabric o.p.s.
@license: http://www.gnu.org/licenses/gpl-3.0.txt
@author: Gabriel Nistor

Provides the configurations for the processors used in handling the request.
'''

from .encoder_decoder import renderAssembly, modelEncoder
from ally.container import ioc
from ally.core.impl.processor.arguments import ArgumentsPrepareHandler, \
    ArgumentsBuildHandler
from ally.core.impl.processor.invoking import InvokingHandler
from ally.core.impl.processor.method_invoker import MethodInvokerHandler
from ally.core.impl.processor.text_conversion import ConversionSetHandler
from ally.core.spec.resources import Normalizer, Converter
from ally.design.processor import Handler, Assembly
from ally.core.impl.processor.explain_error import ExplainErrorHandler
from ally.core.impl.processor.renderer import RendererHandler
from ally.core.impl.processor.encoder import EncoderHandler

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

# --------------------------------------------------------------------

@ioc.entity
def normalizer() -> Normalizer: return Normalizer()

@ioc.entity
def converter() -> Converter: return Converter()

# --------------------------------------------------------------------

@ioc.entity
def assemblyResources() -> Assembly:
    '''
    The assembly containing the handlers that will be used in processing a REST request.
    '''
    return Assembly()

@ioc.entity
def argumentsPrepare() -> Handler: return ArgumentsPrepareHandler()

@ioc.entity
def methodInvoker() -> Handler: return MethodInvokerHandler()

@ioc.entity
def conversion() -> Handler:
    b = ConversionSetHandler()
    b.normalizer = normalizer()
    b.converter = converter()
    return b

@ioc.entity
def argumentsBuild() -> Handler: return ArgumentsBuildHandler()

@ioc.entity
def invoking() -> Handler: return InvokingHandler()

@ioc.entity
def encoder() -> Handler:
    b = EncoderHandler()
    b.modelEncoder = modelEncoder()
    return b

@ioc.entity
def explainError(): return ExplainErrorHandler()

@ioc.entity
def renderer() -> Handler:
    b = RendererHandler()
    b.charSetDefault = default_characterset()
    b.renderAssembly = renderAssembly()
    return b

# --------------------------------------------------------------------

@ioc.before(assemblyResources)
def updateAssemblyResourcesForCore():
    assemblyResources().add(argumentsPrepare(), renderer(), methodInvoker(), conversion(), argumentsBuild(), invoking(),
                            encoder(), explainError())
