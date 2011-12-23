'''
Created on Nov 24, 2011

@package: Newscoop
@copyright: 2011 Sourcefabric o.p.s.
@license: http://www.gnu.org/licenses/gpl-3.0.txt
@author: Gabriel Nistor

Provides the configurations for the encoders and decoders for parameters.
'''

from ally.core.impl.encdec_param import EncDecPrimitives, EncDecQuery

# --------------------------------------------------------------------
# Creating the parameters encoders and decoders

def encDecPrimitives(converterPath) -> EncDecPrimitives:
    b = EncDecPrimitives(); yield b
    b.converterPath = converterPath

def encDecQuery(converterPath) -> EncDecQuery:
    b = EncDecQuery(); yield b
    b.converterPath = converterPath

# ---------------------------------

decodersParameters = lambda ctx: [ctx.encDecPrimitives, ctx.encDecQuery]
