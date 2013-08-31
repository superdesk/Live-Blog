'''
Created on Jan 23, 2013

@package: superdesk security
@copyright: 2012 Sourcefabric o.p.s.
@license: http://www.gnu.org/licenses/gpl-3.0.txt
@author: Gabriel Nistor

Provides the gateway service setup patch.
'''

from ally.container import ioc
from ally.support.api.util_service import nameForModel
from gateway.api.gateway import Gateway
from security.api.domain_security import DOMAIN
from superdesk.security.api.authentication import Login
import logging

# --------------------------------------------------------------------

log = logging.getLogger(__name__)

# --------------------------------------------------------------------

try:
    from __setup__ import ally_gateway  # @UnusedImport
    from __setup__ import ally_core_http  # @UnusedImport
except ImportError: log.info('No gateway service available, thus no need to publish the authorized gateway URI')
else:
    from __setup__.ally_gateway.processor import gateway_authorized_uri
    from __setup__.ally_core_http.server import root_uri_resources
    
    @ioc.replace(gateway_authorized_uri)
    def user_gateway_authorized_uri():
        '''
        The authenticated user base access root URI.
        '''
        return '/'.join((root_uri_resources(), DOMAIN + nameForModel(Login), '%s', nameForModel(Gateway)))
