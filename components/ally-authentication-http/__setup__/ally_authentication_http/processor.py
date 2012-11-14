'''
Created on Nov 24, 2011

@package: ally authentication http
@copyright: 2012 Sourcefabric o.p.s.
@license: http://www.gnu.org/licenses/gpl-3.0.txt
@author: Gabriel Nistor

Provides the configurations for the authentication processors.
'''

from ..ally_authentication_core.resources import resourcesLocatorAuthentication
from ..ally_core.processor import assemblyResources, argumentsBuild
from ..ally_core_http.processor import converterPath, uri, redirect, \
    assemblyRedirect, pathAssemblies, parameter
from ally.container import ioc
from ally.core.authentication.impl.processor.authentication import \
    AuthenticationHandler
from ally.core.http.impl.processor.redirect import RedirectHandler
from ally.core.http.impl.processor.uri import URIHandler
from ally.design.processor import Handler, Assembly

# --------------------------------------------------------------------

@ioc.config
def server_pattern_authenticated():
    ''' The pattern used for matching the REST authenticated resources paths in HTTP URL's'''
    return '^resources\/my(/|(?=\\.)|$)'

@ioc.config
def always_authenticate():
    '''
    Flag indicating that the authentication should not be made only when there is a authentication data type required,
    but the authentication should be made for all requests
    '''
    return False

# --------------------------------------------------------------------

@ioc.entity
def uriAuthentication() -> Handler:
    b = URIHandler()
    b.resourcesLocator = resourcesLocatorAuthentication()
    b.converterPath = converterPath()
    return b

@ioc.entity
def redirectAuthentication() -> Handler:
    b = RedirectHandler()
    b.redirectAssembly = assemblyRedirectAuthentication()
    return b

@ioc.entity
def authentication() -> Handler:
    b = AuthenticationHandler()
    b.alwaysAuthenticate = always_authenticate()
    b.authenticators = authenticators()
    return b

# --------------------------------------------------------------------

@ioc.entity
def assemblyResourcesAuthentication() -> Assembly:
    '''
    The assembly containing the handlers that will be used in processing a REST request.
    '''
    return Assembly()

@ioc.entity
def assemblyRedirectAuthentication() -> Assembly:
    '''
    The assembly containing the handlers that will be used in processing a redirect.
    '''
    return Assembly()

@ioc.entity
def authenticators(): return []

# --------------------------------------------------------------------

@ioc.before(assemblyResourcesAuthentication)
def updateAssemblyResourcesAuthentication():
    assemblyResourcesAuthentication().add(assemblyResources())
    assemblyResourcesAuthentication().replace(uri(), uriAuthentication())
    assemblyResourcesAuthentication().replace(redirect(), redirectAuthentication())
    assemblyResourcesAuthentication().add(authentication(), before=parameter())

@ioc.before(assemblyRedirectAuthentication)
def updateAssemblyRedirectAuthentication():
    assemblyRedirectAuthentication().add(assemblyRedirect())
    assemblyRedirectAuthentication().add(authentication(), before=argumentsBuild())

@ioc.before(pathAssemblies)
def updatePathAssemblies():
    pathAssemblies().insert(0, (server_pattern_authenticated(), assemblyResourcesAuthentication()))

