'''
Created on Nov 24, 2011

@package: Newscoop
@copyright: 2011 Sourcefabric o.p.s.
@license: http://www.gnu.org/licenses/gpl-3.0.txt
@author: Gabriel Nistor

Provides the configurations for the processors used in handling the request.
'''

from ally import ioc
from ally.core.http.processor.header import HeaderStandardHandler
from ally.core.http.processor.header_x import HeaderXHandler
from ally.core.http.processor.uri import URIHandler

# --------------------------------------------------------------------
# Creating the processors used in handling the request
    
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

def headerX(contentNormalizer, _readFromParams) -> HeaderXHandler:
    b = HeaderXHandler()
    b.normalizer = contentNormalizer
    b.readFromParams = _readFromParams
    return b

# ---------------------------------

@ioc.before
def updateHandlersExplainError(ctx, handlersExplainError):
    handlersExplainError.insert(0, ctx.headerStandard)

# ---------------------------------

handlers = lambda ctx: [ctx.explainError, ctx.uri, ctx.headerStandard, ctx.methodInvoker, ctx.headerX, ctx.converter,
                        ctx.requestTypes, ctx.parameters, ctx.decoding, ctx.invokingHandler, ctx.encoding]
