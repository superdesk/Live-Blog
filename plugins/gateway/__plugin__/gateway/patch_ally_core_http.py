'''
Created on Feb 19, 2013

@package: gateway
@copyright: 2012 Sourcefabric o.p.s.
@license: http://www.gnu.org/licenses/gpl-3.0.txt
@author: Gabriel Nistor

Provides the ally core http setup patch.
'''

from .service import default_gateways
from ally.container import ioc
import logging

# --------------------------------------------------------------------

log = logging.getLogger(__name__)

# --------------------------------------------------------------------

try:
    from __setup__ import ally_core_http
except ImportError: log.info('No ally core http service available, thus no need to create configurations based on it')
else:
    ally_core_http = ally_core_http  # Just to avoid the import warning
    # ----------------------------------------------------------------
    
    from __setup__.ally_core_http.processor_error import statusToCode
    from __setup__.ally_core_http.server import server_pattern_resources, \
        server_pattern_errors, server_provide_errors
    from ally.http.spec.codes import METHOD_NOT_AVAILABLE, PATH_NOT_FOUND, \
        UNAUTHORIZED_ACCESS, FORBIDDEN_ACCESS, INVALID_AUTHORIZATION
    from ally.http.spec.server import HTTP_OPTIONS
    
    @ioc.before(statusToCode)
    def updateStatusToCodeForGateway():
        statusToCode().update({
                               UNAUTHORIZED_ACCESS.status: UNAUTHORIZED_ACCESS,
                               FORBIDDEN_ACCESS.status: FORBIDDEN_ACCESS,
                               })
    
    ioc.doc(server_pattern_errors, '''
    !Attention if you change this configuration you need also to adjust the 'default_gateways' configuration
    ''')
    
    @ioc.before(default_gateways)
    def updateGatewayWithResourcesOptions():
        default_gateways().extend([
                                   {
                                    'Pattern': server_pattern_resources(),
                                    'Methods': [HTTP_OPTIONS],
                                    },
                                   ])
    
    @ioc.before(default_gateways)
    def updateGatewayWithResourcesErrors():
        if server_provide_errors():
            default_gateways().extend([
                                       # If path is not found then we try to dispatch a unauthorized access if the path is not
                                       # found in REST the default error will have priority over the unauthorized access
                                       {
                                        'Pattern': server_pattern_resources(),
                                        'Errors': [PATH_NOT_FOUND.status],
                                        'Navigate': 'error/{1}?status=%s' % UNAUTHORIZED_ACCESS.status,
                                        },
                                       {
                                        'Pattern': server_pattern_resources(),
                                        'Errors': [INVALID_AUTHORIZATION.status, FORBIDDEN_ACCESS.status, METHOD_NOT_AVAILABLE.status],
                                        'Navigate': 'error/{1}',
                                        },
                                       ])
