'''
Created on Nov 23, 2011

@package: ally http
@copyright: 2012 Sourcefabric o.p.s.
@license: http://www.gnu.org/licenses/gpl-3.0.txt
@author: Gabriel Nistor

Provides the Mongrel2 web server plugins patch for the cdm.
'''

from ..ally_http import server_type
from ally.container import ioc, support
import logging

# --------------------------------------------------------------------

log = logging.getLogger(__name__)

# --------------------------------------------------------------------

try: from .. import ally_cdm
except ImportError: log.info('No local CDM service to stop from delivering content')
else:
    ally_cdm = ally_cdm  # Just to avoid the import warning
    # ----------------------------------------------------------------
    
    from ..ally_cdm.server import server_provide_content
    
    ioc.doc(server_provide_content, '''
    !Attention, if the mongrel2 server is selected this option will always be "false"
    ''')
    
    @ioc.before(server_provide_content, auto=False)
    def server_provide_content_force():
        if server_type() == 'mongrel2': support.force(server_provide_content, False)
