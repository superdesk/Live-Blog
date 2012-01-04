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
from ally.core.spec.server import EncoderParams, DecoderParams

# --------------------------------------------------------------------
# Creating the parameters encoders and decoders

@ioc.entity
def encoderPrimitives() -> EncoderParams:
    b = EncDecPrimitives(); yield b
    b.converterPath = converterPath()

@ioc.entity
def encoderQuery() -> EncoderParams:
    b = EncDecQuery(); yield b
    b.converterPath = converterPath()

@ioc.entity
def decoderPrimitives() -> DecoderParams: return encoderPrimitives()

@ioc.entity
def decoderQuery() -> DecoderParams: return encoderQuery()
    
# ---------------------------------

@ioc.entity
def decodersParameters(): return [decoderPrimitives(), decoderQuery()]
