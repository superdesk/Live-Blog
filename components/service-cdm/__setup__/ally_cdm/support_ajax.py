'''
Created on Nov 24, 2011

@package: service CDM
@copyright: 2012 Sourcefabric o.p.s.
@license: http://www.gnu.org/licenses/gpl-3.0.txt
@author: Gabriel Nistor

Provides the javascript setup required by browser for ajax.
'''

from .processor import updateAssemblyContent, assemblyContent, contentDelivery
from ally.container import ioc
from ally.design.processor.handler import Handler
from ally.http.impl.processor.headers.set_fixed import HeaderSetEncodeHandler
from ally.http.impl.processor.method_deliver_ok import DeliverOkForMethodHandler
from ally.http.spec.server import HTTP_OPTIONS

# --------------------------------------------------------------------

@ioc.config
def ajax_cross_domain() -> bool:
    '''Indicates that the server should also be able to support cross domain ajax requests'''
    return True

@ioc.config
def headers_ajax() -> dict:
    '''The ajax specific headers required by browser for cross domain calls'''
    return {
            'Access-Control-Allow-Origin':['*'],
            } 

# --------------------------------------------------------------------

@ioc.entity
def headerSetAjax() -> Handler:
    b = HeaderSetEncodeHandler()
    b.headers = headers_ajax()
    return b

@ioc.entity
def deliverOkForOptionsHandler() -> Handler:
    b = DeliverOkForMethodHandler()
    b.forMethod = HTTP_OPTIONS
    return b

# --------------------------------------------------------------------

@ioc.after(updateAssemblyContent)
def updateAssemblyContentAjax():
    if ajax_cross_domain():
        assemblyContent().add(headerSetAjax(), deliverOkForOptionsHandler(), before=contentDelivery())
