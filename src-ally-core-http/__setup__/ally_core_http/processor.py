'''
Created on Nov 24, 2011

@package: Newscoop
@copyright: 2011 Sourcefabric o.p.s.
@license: http://www.gnu.org/licenses/gpl-3.0.txt
@author: Gabriel Nistor

Provides the configurations for the processors used in handling the request.
'''

from . import serverRoot
from ..ally_core.converter import contentNormalizer, converterPath
from ..ally_core.processor import explainError, methodInvoker, converter, \
    requestTypes, parameters, decoding, invokingHandler, encoding, \
    handlersExplainError
from ..ally_core.resource_manager import resourcesManager
from ally import ioc
from ally.core.http.processor.header import HeaderStandardHandler
from ally.core.http.processor.header_x import HeaderXHandler
from ally.core.http.processor.uri import URIHandler

# --------------------------------------------------------------------
# Creating the processors used in handling the request

@ioc.entity
def uri() -> URIHandler:
    b = URIHandler()
    b.resourcesManager = resourcesManager()
    b.converterPath = converterPath()
    if serverRoot(): b.urlRoot = serverRoot() + '/'
    return b

readFromParams = ioc.config(lambda:True, 'If true will also read header values that are provided as query parameters')

@ioc.entity   
def headerStandard() -> HeaderStandardHandler:
    b = HeaderStandardHandler()
    b.readFromParams = readFromParams()
    return b

@ioc.entity
def headerX() -> HeaderXHandler:
    b = HeaderXHandler()
    b.normalizer = contentNormalizer()
    b.readFromParams = readFromParams()
    return b

# ---------------------------------

@ioc.before(handlersExplainError)
def updateHandlersExplainError():
    handlersExplainError().insert(0, headerStandard())

# ---------------------------------

handlers = ioc.entity(lambda: [explainError(), uri(), headerStandard(), methodInvoker(), headerX(), converter(),
                               requestTypes(), parameters(), decoding(), invokingHandler(), encoding()])
