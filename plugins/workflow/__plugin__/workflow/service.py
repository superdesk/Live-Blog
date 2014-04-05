'''
Created on Jan 9, 2012

@package: workflow
@copyright: 2012 Sourcefabric o.p.s.
@license: http://www.gnu.org/licenses/gpl-3.0.txt
@author: Gabriel Nistor

Contains the services for workflow.
'''

from ..plugin.registry import registerService
from .database import binders
from ally.container import support, bind, ioc
from ally.design.processor.assembly import Assembly

# --------------------------------------------------------------------

SERVICES = 'workflow.api.**.I*Service'

bind.bindToEntities('workflow.impl.**.*Alchemy', binders=binders)
support.createEntitySetup('workflow.impl.**.*')
support.listenToEntities(SERVICES, listeners=registerService)
support.loadAllEntities(SERVICES)

# --------------------------------------------------------------------

deskHandler = copyTasting = support.notCreated

support.createEntitySetup('workflow.core.impl.processor.**.*')

# --------------------------------------------------------------------

@ioc.entity
def workflows() -> list: return ['Copy Tasting']

@ioc.entity
def assemblyGraph() -> Assembly:
    return Assembly('Graph nodes')

@ioc.entity
def assemblyWorkflow() -> Assembly:
    return Assembly('Graph workflow nodes')

# --------------------------------------------------------------------

@ioc.before(assemblyGraph)
def updateAssemblyGraph():
    assemblyGraph().add(deskHandler())
    
@ioc.before(assemblyWorkflow)
def updateAssemblyWorkflow():
    assemblyWorkflow().add(copyTasting())