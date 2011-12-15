'''
Created on Nov 24, 2011

@package: Newscoop
@copyright: 2011 Sourcefabric o.p.s.
@license: http://www.gnu.org/licenses/gpl-3.0.txt
@author: Gabriel Nistor

Provides the configurations for the assemblers.
'''

from ally.core.impl.assembler import AssembleGet, AssembleInsert, AssembleUpdate, \
    AssembleDelete

# --------------------------------------------------------------------
# Creating the assemblers

def assembleGet() -> AssembleGet: return AssembleGet()

def assembleDelete() -> AssembleDelete: return AssembleDelete()

def assembleInsert(contentNormalizer):
    b = AssembleInsert();
    b.normalizer = contentNormalizer
    return b

def assembleUpdate(contentNormalizer):
    b = AssembleUpdate();
    b.normalizer = contentNormalizer
    return b

# ---------------------------------

assemblers = lambda ctx: [ctx.assembleGet, ctx.assembleInsert, ctx.assembleUpdate, ctx.assembleDelete]
