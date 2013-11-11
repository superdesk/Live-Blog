'''
Created on Feb 19, 2013

@package: content
@copyright: 2012 Sourcefabric o.p.s.
@license: http://www.gnu.org/licenses/gpl-3.0.txt
@author: Gabriel Nistor

Provides the ally core setup patch.
'''

import logging

from ally.container import ioc
from ally.design.processor.handler import Handler
from content.base.api.item import Item


# --------------------------------------------------------------------
log = logging.getLogger(__name__)

# --------------------------------------------------------------------

try:
    from __setup__ import ally_core  # @UnusedImport
except ImportError: log.info('No ally core component available, thus no content item model merging is possible')
else:
    from __setup__.ally_core.resources import assemblyAssembler, updateAssemblyAssembler, processMethod
    from ally.core.impl.processor.assembler.model_merger import ModelMergerHandler
   
    @ioc.entity
    def contentItemMerger() -> Handler:
        b = ModelMergerHandler()
        b.base = Item
        return b

    # --------------------------------------------------------------------
    
    @ioc.after(updateAssemblyAssembler)
    def updateAssemblyAssemblerForContentItemMerging():
        assemblyAssembler().add(contentItemMerger(), before=processMethod())
