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

assembleGet = ioc.entity(lambda: AssembleGet(), AssembleGet)

assembleDelete = ioc.entity(lambda: AssembleDelete(), AssembleDelete)

@ioc.entity
def assembleInsert():
    b = AssembleInsert();
    b.normalizer = contentNormalizer()
    return b

@ioc.entity
def assembleUpdate():
    b = AssembleUpdate();
    b.normalizer = contentNormalizer()
    return b

# ---------------------------------

assemblers = ioc.entity(lambda: [assembleGet(), assembleInsert(), assembleUpdate(), assembleDelete()])
