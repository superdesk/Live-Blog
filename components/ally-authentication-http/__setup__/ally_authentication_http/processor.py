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
from ..ally_core.processor import handlersRedirect, redirect, handlersResources, \
    parameters
from ..ally_core_http.processor import handlersFetching, pathProcessors, uri, \
    read_from_params
from ally.container import ioc
from ally.core.authentication.impl.processor.authenticator import \
    AuthenticationHandler
from ally.core.http.impl.processor.uri import URIHandler
from ally.core.impl.processor.redirect import RedirectHandler
from ally.core.spec.server import Processors, Processor
import re
from __setup__.ally_core.resource_management import resourcesRegister
from datetime import timedelta

# --------------------------------------------------------------------

@ioc.config
def server_pattern_authenticated():
    ''' The pattern used for matching the REST authenticated resources paths in HTTP URL's'''
    return '^resources\/my(/|(?=\\.)|$)'

@ioc.config
def login_token_timeout():
    ''' The number of seconds after which the login token expires. '''
    return timedelta(seconds=10)

@ioc.config
def session_token_timeout():
    ''' The number of seconds after which the session expires. '''
    return timedelta(seconds=3600)

# --------------------------------------------------------------------

@ioc.entity
def uriAuthentication() -> Processor:
    b = URIHandler()
    b.resourcesLocator = resourcesLocatorAuthentication()
    b.converterPath = converterPath()
    return b

@ioc.entity
def redirectAuthentication() -> Processor:
    b = RedirectHandler()
    b.redirects = Processors(*handlersRedirectAuthentication())
    return b
#TODO: see hot to incorporate the auth in fetch
#@ioc.entity
#def metaFilterAuthentication() -> Processor:
#    b = MetaFilterHandler()
#    b.normalizer = contentNormalizer()
#    b.fetching = Processors(*handlersFetchingAuthentication())
#    b.readFromParams = read_from_params()
#    return b

@ioc.entity
def authentication() -> Processor:
    b = AuthenticationHandler()
    b.readFromParams = read_from_params()
    b.resourcesRegister = resourcesRegister()
    return b

# --------------------------------------------------------------------

@ioc.entity
def handlersRedirectAuthentication():
    '''
    The handlers that will be used in processing a redirect.
    '''
    handlers = list(handlersRedirect())
    # Adding the authentication handler
    handlers.insert(handlers.index(parameters()), authentication())
    return handlers

@ioc.entity
def handlersResourcesAuthentication():
    handlers = list(handlersResources())

    # Changing the handlers that have been altered for authentication 
    handlers.insert(handlers.index(uri()), uriAuthentication())
    handlers.remove(uri())

    handlers.insert(handlers.index(redirect()), redirectAuthentication())
    handlers.remove(redirect())

#TODO: see how to incorporate the auth in fetch
#    handlers.insert(handlers.index(metaFilter()), metaFilterAuthentication())
#    handlers.remove(metaFilter())

    # Adding the authentication handler
    handlers.insert(handlers.index(parameters()), authentication())
    return handlers

@ioc.entity
def handlersFetchingAuthentication():
    handlers = list(handlersFetching())
    # Adding the authentication handler
    handlers.insert(handlers.index(parameters()), authentication())
    return handlers

# --------------------------------------------------------------------

@ioc.before(pathProcessors)
def updatePathProcessors():
    processors = Processors(*handlersResourcesAuthentication())
    pathProcessors().insert(0, (re.compile(server_pattern_authenticated()), processors))

