'''
Created on Feb 19, 2013

@package: superdesk security
@copyright: 2012 Sourcefabric o.p.s.
@license: http://www.gnu.org/licenses/gpl-3.0.txt
@author: Gabriel Nistor

Provides the ally core http setup patch.
'''

from . import service
from ally.container import ioc, support
from ally.container.support import nameInEntity
from superdesk.security.impl.authentication import AuthenticationServiceAlchemy
import logging

# --------------------------------------------------------------------

log = logging.getLogger(__name__)

# --------------------------------------------------------------------

try:
    from __setup__ import ally_core_http
except ImportError: log.info('No ally core http service available, thus cannot populate configurations')
else:
    ally_core_http = ally_core_http  # Just to avoid the import warning
    # ----------------------------------------------------------------
    
    from __setup__.ally_core_http.processor import root_uri_resources

    root_uri = ioc.entityOf(nameInEntity(AuthenticationServiceAlchemy, 'root_uri'), module=service)
    ioc.doc(root_uri, '''
        !Attention, this is automatically set to the server resources root. 
        ''')
    
    @ioc.before(root_uri, auto=False)
    def root_uri_force():
        support.force(root_uri, root_uri_resources())
