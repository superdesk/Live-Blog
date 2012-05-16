'''
Created on Nov 24, 2011

@package: ally authentication http
@copyright: 2012 Sourcefabric o.p.s.
@license: http://www.gnu.org/licenses/gpl-3.0.txt
@author: Gabriel Nistor

Provides the configurations for the authentication processors.
'''

from ..ally_authentication_core.resource_management import \
    resourcesLocatorAuthentication
from ..ally_core.converter import converterPath
from ..ally_core.processor import handlersResources, parameters
from ..ally_core_http.processor import pathProcessors, uri, read_from_params
from ally.container import ioc
from ally.core.authentication.impl.processor.authenticator import \
    AuthenticationHandler
from ally.core.http.impl.processor.uri import URIHandler
from ally.core.spec.server import Processors, Processor
import re

# --------------------------------------------------------------------

@ioc.entity
def uriAuthentication() -> Processor:
    b = URIHandler()
    b.resourcesLocator = resourcesLocatorAuthentication()
    b.converterPath = converterPath()
    return b

@ioc.entity
def authentication() -> Processor:
    b = AuthenticationHandler()
    b.readFromParams = read_from_params()
    return b

@ioc.entity
def handlersResourcesAuthentication():
    handlers = list(handlersResources())
    handlers.insert(handlers.index(uri()), uriAuthentication())
    handlers.remove(uri())
    handlers.insert(handlers.index(parameters()), authentication())
    return handlers

# --------------------------------------------------------------------

@ioc.before(pathProcessors)
def updatePathProcessors():
    pathProcessors().append((re.compile('^authenticated(/|(?=\\.)|$)'), Processors(*handlersResourcesAuthentication())))

