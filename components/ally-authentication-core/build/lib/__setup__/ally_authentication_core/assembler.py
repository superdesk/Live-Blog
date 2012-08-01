'''
Created on Nov 24, 2011

@package: ally authentication core
@copyright: 2012 Sourcefabric o.p.s.
@license: http://www.gnu.org/licenses/gpl-3.0.txt
@author: Gabriel Nistor

Provides the configurations for the authentication assemblers.
'''

from ..ally_core.assembler import assemblers
from ally.container import ioc
from ally.core.authentication.impl.assembler import AssembleAuthenticated
from ally.core.spec.resources import IAssembler

# --------------------------------------------------------------------
# Creating the assemblers

@ioc.entity
def assembleAuthenticated() -> IAssembler: return AssembleAuthenticated()

# ---------------------------------

@ioc.entity
def assemblersAuthentication():
    b = [assembleAuthenticated()]
    b.extend(assemblers())
    return b
