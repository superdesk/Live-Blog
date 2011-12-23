'''
Created on Nov 24, 2011

@package: Newscoop
@copyright: 2011 Sourcefabric o.p.s.
@license: http://www.gnu.org/licenses/gpl-3.0.txt
@author: Gabriel Nistor

Provides the the javascript setup required by browser for ajax.
'''

from ally.core.impl.processor.deliver_ok import DeliverOkHandler
from ally.core.http.impl.encoder_header_set import EncoderHeaderSet
from ally.core.http.spec import METHOD_OPTIONS
from ally import ioc

# --------------------------------------------------------------------
# Service handlers

def encoderHeaderSet(_headersAjax:'The ajax specific headers required by browser for cross domain calls'={
                       'Access-Control-Allow-Origin':'*',
                       'Access-Control-Allow-Headers':'X-Filter',
                       }) -> EncoderHeaderSet:
    b = EncoderHeaderSet()
    b.headers = _headersAjax
    return b

def deliverOkHandler(handlers, methodInvoker) -> DeliverOkHandler:
    b = DeliverOkHandler()
    b.forMethod = METHOD_OPTIONS
    return b

@ioc.onlyIf(_ajaxCrossDomain=True, doc='Indicates that the server should also be able to support cross domain ajax '
            'requests')
@ioc.before('handlers')
def updateHandlers(handlers, methodInvoker, deliverOkHandler):
    handlers.insert(handlers.index(methodInvoker), deliverOkHandler)

@ioc.onlyIf(_ajaxCrossDomain=True)
@ioc.before('encodersHeader')
def updateEncodersHeader(encodersHeader, encoderHeaderSet):
    encodersHeader.append(encoderHeaderSet)
