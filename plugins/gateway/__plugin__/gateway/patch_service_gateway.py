'''
Created on Jan 23, 2013

@package: gateway
@copyright: 2012 Sourcefabric o.p.s.
@license: http://www.gnu.org/licenses/gpl-3.0.txt
@author: Gabriel Nistor

Provides the gateway service setup patch.
'''

from ally.container import ioc
import logging

# --------------------------------------------------------------------

log = logging.getLogger(__name__)

# --------------------------------------------------------------------

try:
    from __setup__ import ally_gateway
    from __setup__ import ally_core_http
except ImportError: log.info('No gateway service available, thus no need to publish the gateway data')
else:
    ally_gateway = ally_gateway  # Just to avoid the import warning
    ally_core_http = ally_core_http  # Just to avoid the import warning
    # ----------------------------------------------------------------
    
    from __setup__.ally_gateway.processor import gateway_uri
    from __setup__.ally_core_http.processor import root_uri_resources
    
    @ioc.replace(gateway_uri)
    def gateway_uri_anonymous():
        '''
        The anonymous gateway URI.
        '''
        return root_uri_resources() % 'Gateway'

