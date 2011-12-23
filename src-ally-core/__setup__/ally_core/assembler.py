'''
Created on Nov 24, 2011

@package: Newscoop
@copyright: 2011 Sourcefabric o.p.s.
@license: http://www.gnu.org/licenses/gpl-3.0.txt
@author: Gabriel Nistor

Provides the configurations for the assemblers.
'''

from .converter import contentNormalizer
from ally import ioc
from ally.core.impl.assembler import AssembleGet, AssembleInsert, AssembleUpdate, \
    AssembleDelete

# --------------------------------------------------------------------
# Creating the assemblers

@ioc.entity
def assembleGet() -> AssembleGet: return AssembleGet()

@ioc.entity
def assembleDelete() -> AssembleDelete: return AssembleDelete()

@ioc.entity
def assembleInsert() -> AssembleInsert:
    b = AssembleInsert();
    b.normalizer = contentNormalizer()
    return b

@ioc.entity
def assembleUpdate() -> AssembleUpdate:
    b = AssembleUpdate();
    b.normalizer = contentNormalizer()
    return b

# ---------------------------------

@ioc.entity
def assemblers():
    return [assembleGet(), assembleInsert(), assembleUpdate(), assembleDelete()]
