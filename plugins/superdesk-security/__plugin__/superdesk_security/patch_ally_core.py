'''
Created on Feb 26, 2013

@package: superdesk security
@copyright: 2012 Sourcefabric o.p.s.
@license: http://www.gnu.org/licenses/gpl-3.0.txt
@author: Gabriel Nistor

Provides the ally core setup patch.
'''

from ally.container import support, ioc
import logging

# --------------------------------------------------------------------

log = logging.getLogger(__name__)

# --------------------------------------------------------------------

try:
    from __setup__ import ally_core  # @UnusedImport
except ImportError: log.info('No ally core component available, thus no need to register user ACL assemblers to it')
else:
    from __setup__.ally_core.resources import assemblyAssembler
    from ..gateway_acl.patch_ally_core import indexFilter, updateAssemblyAssemblerForAccess
    from superdesk.security.core.impl.processor import assembler

    # The assembler processors
    filterUserInject = support.notCreated  # Just to avoid errors
    support.createEntitySetup(assembler)
    
    # ----------------------------------------------------------------
    
    @ioc.after(updateAssemblyAssemblerForAccess)
    def updateAssemblyAssemblerForUserFilterInject():
        assemblyAssembler().add(filterUserInject(), before=indexFilter())
