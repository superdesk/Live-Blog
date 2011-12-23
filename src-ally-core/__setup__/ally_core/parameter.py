'''
Created on Nov 24, 2011

@package: Newscoop
@copyright: 2011 Sourcefabric o.p.s.
@license: http://www.gnu.org/licenses/gpl-3.0.txt
@author: Gabriel Nistor

Provides the configurations for the encoders and decoders for parameters.
'''

from .converter import converterPath
from ally import ioc
from ally.core.impl.encdec_param import EncDecPrimitives, EncDecQuery

# --------------------------------------------------------------------
# Creating the parameters encoders and decoders

@ioc.entity
def encDecPrimitives() -> EncDecPrimitives:
    b = EncDecPrimitives(); yield b
    b.converterPath = converterPath()

@ioc.entity
def encDecQuery() -> EncDecQuery:
    b = EncDecQuery(); yield b
    b.converterPath = converterPath()

# ---------------------------------

@ioc.entity
def decodersParameters(): return [encDecPrimitives(), encDecQuery()]
