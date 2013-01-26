'''
Created on Jan 23, 2013

@package: superdesk security
@copyright: 2012 Sourcefabric o.p.s.
@license: http://www.gnu.org/licenses/gpl-3.0.txt
@author: Gabriel Nistor

Provides the security service setup patch.
'''

from ally.container import ioc
import logging

# --------------------------------------------------------------------

log = logging.getLogger(__name__)

# --------------------------------------------------------------------

try: from __setup__ import security
except ImportError: log.info('No security service available, thus no need to publish the access data')
else:
    security = security  # Just to avoid the import warning
    # ----------------------------------------------------------------
    
    from __setup__.security.processor import access_uri_root, access_uri
    
    @ioc.replace(access_uri_root)
    def user_access_uri_root():
        '''
        The authenticated user base access root URI.
        '''
        return 'resources/'
    
    @ioc.replace(access_uri)
    def user_access_uri():
        '''
        The authenticated user base access URI.
        '''
        return 'Security/Login/*/Access'

