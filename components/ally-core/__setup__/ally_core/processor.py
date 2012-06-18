'''
Created on Nov 24, 2011

@package: ally core
@copyright: 2012 Sourcefabric o.p.s.
@license: http://www.gnu.org/licenses/gpl-3.0.txt
@author: Gabriel Nistor

Provides the configurations for the processors used in handling the request.
'''

from ally.container import ioc
from ally.core.impl.processor.invoking import InvokingHandler
from ally.core.impl.processor.method_invoker import MethodInvokerHandler
from ally.core.impl.processor.text_conversion import ConversionSetHandler
from ally.core.spec.resources import Normalizer, Converter
from ally.design.processor import Handler, Assembly
from ally.core.impl.processor.arguments import ArgumentsOfTypeHandler, \
    ArgumentsBuildHandler

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
def resourcesAssembly() -> Assembly:
    '''
    The assembly containing the handlers that will be used in processing a REST request.
    '''
    return Assembly()

@ioc.entity
def normalizer() -> Normalizer: return Normalizer()

@ioc.entity
def converter() -> Converter: return Converter()

# --------------------------------------------------------------------

@ioc.entity
def methodInvoker() -> Handler: return MethodInvokerHandler()

@ioc.entity
def conversion() -> Handler:
    b = ConversionSetHandler()
    b.normalizer = normalizer()
    b.converter = converter()
    return b

@ioc.entity
def argumentsOfType() -> Handler: return ArgumentsOfTypeHandler()

@ioc.entity
def argumentsBuild() -> Handler: return ArgumentsBuildHandler()

@ioc.entity
def invoking() -> Handler: return InvokingHandler()

# --------------------------------------------------------------------

@ioc.before(resourcesAssembly)
def updateResourcesAssembly():
    resourcesAssembly().add(argumentsOfType(), methodInvoker(), conversion(), argumentsBuild(), invoking())
