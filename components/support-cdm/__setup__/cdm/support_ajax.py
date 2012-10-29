'''
Created on Nov 24, 2011

@package: support cdm
@copyright: 2012 Sourcefabric o.p.s.
@license: http://www.gnu.org/licenses/gpl-3.0.txt
@author: Gabriel Nistor

Provides the javascript setup required by browser for ajax.
'''

from ..ally_core_http.support_ajax import ajax_cross_domain, deliverOkHandler
from ..cdm.processor import updateAssemblyContent, assemblyContent, \
    contentDelivery
from ally.container import ioc
from ally.core.http.impl.processor.headers.set_fixed import \
    HeaderSetEncodeHandler
from ally.design.processor import Handler

# --------------------------------------------------------------------

@ioc.config
def headers_ajax_cdm() -> dict:
    '''The ajax specific headers required by browser for cross domain calls'''
    return {
            'Access-Control-Allow-Origin': ['*'],
            }

# --------------------------------------------------------------------

@ioc.entity
def headerSetEncodeCdm() -> Handler:
    b = HeaderSetEncodeHandler()
    b.headers = headers_ajax_cdm()
    return b

@ioc.after(updateAssemblyContent)
def updateAssemblyContentAjax():
    if ajax_cross_domain():
        assemblyContent().add(headerSetEncodeCdm(), deliverOkHandler(), before=contentDelivery())
