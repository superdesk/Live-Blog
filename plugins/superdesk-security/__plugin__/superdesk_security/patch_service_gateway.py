'''
Created on Jan 23, 2013

@package: superdesk security
@copyright: 2012 Sourcefabric o.p.s.
@license: http://www.gnu.org/licenses/gpl-3.0.txt
@author: Gabriel Nistor

Provides the gateway service setup patch.
'''

from __setup__.ally_core_http.processor import root_uri_resources
from ally.container import ioc
import logging

# --------------------------------------------------------------------

log = logging.getLogger(__name__)

# --------------------------------------------------------------------

try: from __setup__ import ally_gateway
except ImportError: log.info('No gateway service available, thus no need to publish the authorized gateway URI')
else:
    ally_gateway = ally_gateway  # Just to avoid the import warning
    # ----------------------------------------------------------------
    
    from __setup__.ally_gateway.processor import gateway_authorized_uri
    
    @ioc.replace(gateway_authorized_uri)
    def user_gateway_authorized_uri():
        '''
        The authenticated user base access root URI.
        '''
        return root_uri_resources() % 'Security/Login/%s/Gateway'
