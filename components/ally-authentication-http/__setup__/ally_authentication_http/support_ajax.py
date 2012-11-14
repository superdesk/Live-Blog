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

@ioc.after(headers_ajax)
def updateHeadersAjaxAuthorization():
    headers_ajax()['Access-Control-Allow-Headers'].append('Authorization')
