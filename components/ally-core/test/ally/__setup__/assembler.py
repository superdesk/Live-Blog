'''
Created on Nov 24, 2011

@package: Newscoop
@copyright: 2011 Sourcefabric o.p.s.
@license: http://www.gnu.org/licenses/gpl-3.0.txt
@author: Gabriel Nistor

Provides the configurations for the assemblers.
'''

from .converter import contentNormalizer
from ally.container import ioc
from ally.core.impl.assembler import AssembleGet, AssembleInsert, AssembleUpdate, \
    AssembleDelete
from ally.core.spec.resources import IAssembler

# --------------------------------------------------------------------
# Creating the assemblers

@ioc.entity
def assembleGet() -> IAssembler: return AssembleGet()

@ioc.entity
def assembleDelete() -> IAssembler: return AssembleDelete()

@ioc.entity
def assembleInsert() -> IAssembler:
    b = AssembleInsert();
    b.normalizer = contentNormalizer()
    return b

@ioc.entity
def assembleUpdate() -> IAssembler:
    b = AssembleUpdate();
    b.normalizer = contentNormalizer()
    return b

# ---------------------------------

@ioc.entity
def assemblers():
    return [assembleGet(), assembleInsert(), assembleUpdate(), assembleDelete()]
