'''
Created on Jan 25, 2013

@package: ally http
@copyright: 2011 Sourcefabric o.p.s.
@license: http://www.gnu.org/licenses/gpl-3.0.txt
@author: Gabriel Nistor

Provides the setup patch when the server is run with ally core http.
'''

from ..ally_http import server_type
from .processor import asyncoreContent
from .server import SERVER_ASYNCORE
from ally.container import ioc
import logging

# --------------------------------------------------------------------

log = logging.getLogger(__name__)

# --------------------------------------------------------------------

try: from .. import ally_core_http
except ImportError: log.info('No REST core available thus skip the resources patching specific for asyncore')
else:
    ally_core_http = ally_core_http  # Just to avoid the import warning
    # ----------------------------------------------------------------

    from ..ally_core_http.processor import updateAssemblyResources, assemblyResources, parserMultiPart
    
    # ----------------------------------------------------------------
    
    @ioc.after(updateAssemblyResources)
    def updateAssemblyResourcesForHTTPAsyncore():
        if server_type() == SERVER_ASYNCORE:
            assemblyResources().add(asyncoreContent(), before=parserMultiPart())
