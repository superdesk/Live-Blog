'''
Created on Nov 24, 2011

@package: ally authentication http
@copyright: 2012 Sourcefabric o.p.s.
@license: http://www.gnu.org/licenses/gpl-3.0.txt
@author: Gabriel Nistor

Provides updates on the javascript setup required by browser for ajax.
'''

from ..ally_core_http.support_ajax import headers_ajax
from ally.container import ioc

# --------------------------------------------------------------------

@ioc.replace(headers_ajax)
def headers_ajax_authorization():
    return {
            'Access-Control-Allow-Origin':'*',
            'Access-Control-Allow-Headers':'X-Filter, X-HTTP-Method-Override, Authorization',
            }
