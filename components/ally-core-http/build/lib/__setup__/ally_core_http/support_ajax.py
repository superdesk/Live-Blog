'''
Created on Nov 24, 2011

@package: ally core http
@copyright: 2012 Sourcefabric o.p.s.
@license: http://www.gnu.org/licenses/gpl-3.0.txt
@author: Gabriel Nistor

Provides the javascript setup required by browser for ajax.
'''

from ..ally_core.processor import assemblyResources
from ..ally_core_http.processor import uri, updateAssemblyResourcesForHTTP
from ally.container import ioc
from ally.core.http.impl.processor.headers.set_fixed import \
    HeaderSetEncodeHandler
from ally.core.http.spec.server import METHOD_OPTIONS
from ally.core.impl.processor.deliver_ok import DeliverOkHandler
from ally.design.processor import Handler

# --------------------------------------------------------------------

@ioc.config
def ajax_cross_domain() -> bool:
    '''Indicates that the server should also be able to support cross domain ajax requests'''
    return True

@ioc.config
def headers_ajax() -> dict:
    '''The ajax specific headers required by browser for cross domain calls'''
    return {
            'Access-Control-Allow-Origin':'*',
            'Access-Control-Allow-Headers':'X-Filter, X-HTTP-Method-Override',
            }

# --------------------------------------------------------------------

@ioc.entity
def headerSetAjax() -> Handler:
    b = HeaderSetEncodeHandler()
    b.headers = headers_ajax()
    return b

@ioc.entity
def deliverOkHandler() -> Handler:
    b = DeliverOkHandler()
    b.forMethod = METHOD_OPTIONS
    return b

# --------------------------------------------------------------------

@ioc.after(updateAssemblyResourcesForHTTP)
def updateAssemblyResourcesForHTTPAjax():
    if ajax_cross_domain():
        assemblyResources().add(headerSetAjax(), deliverOkHandler(), before=uri())
