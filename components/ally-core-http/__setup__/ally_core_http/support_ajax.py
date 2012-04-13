'''
Created on Nov 24, 2011

@package: ally core http
@copyright: 2012 Sourcefabric o.p.s.
@license: http://www.gnu.org/licenses/gpl-3.0.txt
@author: Gabriel Nistor

Provides the the javascript setup required by browser for ajax.
'''

from ..ally_core.processor import methodInvoker
from ..ally_core_http.encoder_header import encodersHeader
from .processor import handlersResources
from ally.container import ioc
from ally.core.http.impl.encoder_header_set import EncoderHeaderSet
from ally.core.http.spec import METHOD_OPTIONS
from ally.core.impl.processor.deliver_ok import DeliverOkHandler

# --------------------------------------------------------------------

@ioc.config
def ajax_cross_domain() -> bool:
    '''Indicates that the server should also be able to support cross domain ajax requests'''
    return False

@ioc.config
def headers_ajax() -> dict:
    '''The ajax specific headers required by browser for cross domain calls'''
    return {
            'Access-Control-Allow-Origin':'*',
            #TODO: implement proper processor for this quickfix
            'Access-Control-Allow-Headers':'X-Filter, X-HTTP-Method-Override',
            }

# --------------------------------------------------------------------

@ioc.entity
def encoderHeaderSet() -> EncoderHeaderSet:
    b = EncoderHeaderSet()
    b.headers = headers_ajax()
    return b

@ioc.entity
def deliverOkHandler() -> DeliverOkHandler:
    b = DeliverOkHandler()
    b.forMethod = METHOD_OPTIONS
    return b

# --------------------------------------------------------------------

@ioc.before(handlersResources)
def updateHandlersResources():
    if ajax_cross_domain(): handlersResources().insert(handlersResources().index(methodInvoker()), deliverOkHandler())

@ioc.before(encodersHeader)
def updateEncodersHeader():
    if ajax_cross_domain(): encodersHeader().append(encoderHeaderSet())
