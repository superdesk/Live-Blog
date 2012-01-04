'''
Created on Nov 24, 2011

@package: Newscoop
@copyright: 2011 Sourcefabric o.p.s.
@license: http://www.gnu.org/licenses/gpl-3.0.txt
@author: Gabriel Nistor

Provides the the javascript setup required by browser for ajax.
'''

from ..ally_core.processor import methodInvoker
from ..ally_core_http.encoder_header import encodersHeader
from .processor import handlers
from ally import ioc
from ally.core.http.impl.encoder_header_set import EncoderHeaderSet
from ally.core.http.spec import METHOD_OPTIONS
from ally.core.impl.processor.deliver_ok import DeliverOkHandler

# --------------------------------------------------------------------
# Service handlers

@ioc.config
def ajaxCrossDomain() -> bool:
    '''Indicates that the server should also be able to support cross domain ajax requests'''
    return False

@ioc.config
def headersAjax() -> dict: 
    '''The ajax specific headers required by browser for cross domain calls'''
    return {
            'Access-Control-Allow-Origin':'*',
            'Access-Control-Allow-Headers':'X-Filter',
            }

@ioc.entity
def encoderHeaderSet() -> EncoderHeaderSet:
    b = EncoderHeaderSet()
    b.headers = headersAjax()
    return b

@ioc.entity
def deliverOkHandler() -> DeliverOkHandler:
    b = DeliverOkHandler()
    b.forMethod = METHOD_OPTIONS
    return b

@ioc.before(handlers)
def updateHandlers():
    if ajaxCrossDomain(): handlers().insert(handlers().index(methodInvoker()), deliverOkHandler())

@ioc.before(encodersHeader)
def updateEncodersHeader():
    if ajaxCrossDomain(): encodersHeader().append(encoderHeaderSet())
