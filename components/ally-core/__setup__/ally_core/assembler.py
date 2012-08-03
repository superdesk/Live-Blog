'''
Created on Nov 24, 2011

@package: ally core
@copyright: 2012 Sourcefabric o.p.s.
@license: http://www.gnu.org/licenses/gpl-3.0.txt
@author: Gabriel Nistor

Provides the configurations for the assemblers.
'''

from ally.container import ioc
from ally.core.impl.assembler import AssembleGet, AssembleInsert, AssembleUpdate, \
    AssembleDelete, AssembleUpdateModel
from ally.core.spec.resources import IAssembler

# --------------------------------------------------------------------
# Creating the assemblers

@ioc.entity
def assembleGet() -> IAssembler: return AssembleGet()

@ioc.entity
def assembleDelete() -> IAssembler: return AssembleDelete()

@ioc.entity
def assembleInsert() -> IAssembler: return AssembleInsert()

@ioc.entity
def assembleUpdate() -> IAssembler: return AssembleUpdate()

@ioc.entity
def assembleUpdateModel() -> IAssembler: return AssembleUpdateModel()

# ---------------------------------

@ioc.entity
def assemblers():
    return [assembleGet(), assembleInsert(), assembleUpdateModel(), assembleUpdate(), assembleDelete()]
