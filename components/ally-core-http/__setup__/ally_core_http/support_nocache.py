'''
Created on Sep 13, 2012

@package: ally core http
@copyright: 2012 Sourcefabric o.p.s.
@license: http://www.gnu.org/licenses/gpl-3.0.txt
@author: Gabriel Nistor

Provides the no cache headers support for browsers like IE.
'''

from ..ally_core.processor import assemblyResources
from ..ally_core_http.processor import uri, updateAssemblyResourcesForHTTP
from ally.container import ioc
from ally.core.http.impl.processor.headers.set_fixed import \
    HeaderSetEncodeHandler
from ally.design.processor import Handler

# --------------------------------------------------------------------

@ioc.config
def no_cache() -> bool:
    '''Indicates that the server should send headers indicating that no cache is available (for browsers like IE)'''
    return True

@ioc.config
def headers_no_cache() -> dict:
    '''The headers required by browsers like IE so it will not use caching'''
    return {
            'Cache-Control':'no-cache',
            'Pragma':'no-cache',
            }

# --------------------------------------------------------------------

@ioc.entity
def headerSetNoCache() -> Handler:
    b = HeaderSetEncodeHandler()
    b.headers = headers_no_cache()
    return b

# --------------------------------------------------------------------

@ioc.after(updateAssemblyResourcesForHTTP)
def updateAssemblyResourcesForHTTPNoCache():
    if no_cache():
        assemblyResources().add(headerSetNoCache(), before=uri())
