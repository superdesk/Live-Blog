'''
Created on Nov 24, 2011

@package: Newscoop
@copyright: 2011 Sourcefabric o.p.s.
@license: http://www.gnu.org/licenses/gpl-3.0.txt
@author: Gabriel Nistor

Provides the configurations for the processors used in handling the request.
'''

from . import server_pattern_rest
from ..ally_core import use_old_encdec
from ..ally_core.converter import contentNormalizer, converterPath
from ..ally_core.processor import resourcesHandlers, methodInvoker, converter, \
    handlersExplainError
from ..ally_core.resource_manager import resourcesManager
from ally.container import ioc
from ally.core.http.impl.processor.header import HeaderStandardHandler
from ally.core.http.impl.processor.header_x import HeaderXHandler
from ally.core.http.impl.processor.meta_filter import MetaFilterHandler
from ally.core.http.impl.processor.uri import URIHandler
from ally.core.spec.server import Processor, Processors
import re

# --------------------------------------------------------------------
# Creating the processors used in handling the request

@ioc.entity
def uri() -> Processor:
    b = URIHandler()
    b.resourcesManager = resourcesManager()
    b.converterPath = converterPath()
    return b

@ioc.config
def read_from_params():
    '''If true will also read header values that are provided as query parameters'''
    return True

@ioc.entity
def headerStandard() -> Processor:
    b = HeaderStandardHandler()
    b.readFromParams = read_from_params()
    return b

@ioc.entity
def metaFilter() -> Processor:
    b = MetaFilterHandler()
    b.resourcesManager = resourcesManager()
    b.normalizer = contentNormalizer()
    b.readFromParams = read_from_params()
    return b

@ioc.entity
def headerX() -> Processor:
    #TODO: DEPRECATED: To be removed when the new meta encoders are finalized
    b = HeaderXHandler()
    b.normalizer = contentNormalizer()
    b.readFromParams = read_from_params()
    return b

# ---------------------------------

@ioc.before(handlersExplainError)
def updateHandlersExplainError():
    handlersExplainError().insert(0, headerStandard())

# ---------------------------------

@ioc.before(resourcesHandlers)
def updateHandlers():
    resourcesHandlers().insert(resourcesHandlers().index(methodInvoker()), headerStandard())
    resourcesHandlers().insert(resourcesHandlers().index(headerStandard()), uri())
    if use_old_encdec():
        #TODO: DEPRECATED: To be removed when the new meta encoders are finalized
        resourcesHandlers().insert(resourcesHandlers().index(converter()), headerX())
    else:
        resourcesHandlers().insert(resourcesHandlers().index(converter()), metaFilter())

@ioc.entity
def pathProcessors():
    return [(re.compile(server_pattern_rest()), Processors(*resourcesHandlers()))]
