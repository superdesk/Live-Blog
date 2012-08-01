'''
Created on Nov 24, 2011

@package: ally core http
@copyright: 2011 Sourcefabric o.p.s.
@license: http://www.gnu.org/licenses/gpl-3.0.txt
@author: Gabriel Nistor

Provides the configurations for the processors used in handling the request.
'''

from . import server_pattern_rest
from ..ally_core.converter import contentNormalizer, converterPath
from ..ally_core.processor import handlersResources, methodInvoker, converter, \
    handlersExplainError, requestTypes, parameters, invokingHandler
from ..ally_core.resource_management import resourcesLocator
from ally.container import ioc
from ally.core.http.impl.processor.formatting import FormattingProviderHandler
from ally.core.http.impl.processor.header import HeaderStandardHandler
from ally.core.http.impl.processor.meta_filter import MetaFilterHandler
from ally.core.http.impl.processor.method_override import MethodOverrideHandler
from ally.core.http.impl.processor.uri import URIHandler
from ally.core.spec.server import Processor, Processors
import re

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
def methodOverride() -> Processor:
    b = MethodOverrideHandler()
    b.readFromParams = read_from_params()
    return b

@ioc.entity
def uri() -> Processor:
    b = URIHandler()
    b.resourcesLocator = resourcesLocator()
    b.converterPath = converterPath()
    return b

@ioc.entity
def headerStandard() -> Processor:
    b = HeaderStandardHandler()
    b.readFromParams = read_from_params()
    return b

@ioc.entity
def metaFilter() -> Processor:
    b = MetaFilterHandler()
    b.normalizer = contentNormalizer()
    b.fetching = Processors(*handlersFetching())
    b.readFromParams = read_from_params()
    return b

@ioc.entity
def formattingProvider() -> Processor:
    b = FormattingProviderHandler()
    b.readFromParams = read_from_params()
    return b

@ioc.entity
def pathProcessors():
    return [(re.compile(server_pattern_rest()), Processors(*handlersResources()))]

# --------------------------------------------------------------------

@ioc.entity
def handlersFetching():
    '''
    The specific handlers to be used for an actual invoking procedure, used by the meta filter to actually fetch 
    entities whenever the X-Filter is used and there is no compound method available.
    '''
    return [methodInvoker(), requestTypes(), parameters(), invokingHandler()]

# --------------------------------------------------------------------

@ioc.before(handlersExplainError)
def updateHandlersExplainError():
    handlersExplainError().insert(0, headerStandard())

@ioc.before(handlersResources)
def updateHandlersResources():
    handlers = [uri(), headerStandard(), formattingProvider()]
    if allow_method_override(): handlers.insert(0, methodOverride()) # Add also the method override if so configured
    for proc in handlers: handlersResources().insert(handlersResources().index(methodInvoker()), proc)

    handlersResources().insert(handlersResources().index(converter()), metaFilter())
