'''
Created on Nov 24, 2011

@package: ally core http
@copyright: 2012 Sourcefabric o.p.s.
@license: http://www.gnu.org/licenses/gpl-3.0.txt
@author: Gabriel Nistor

Provides the configurations for encoders and decoders.
'''

from ally.container import ioc
from ally.core.http.impl.encdec.parameter import ParameterDecoderEncoder

# --------------------------------------------------------------------

@ioc.config
def content_types_urlencoded() -> dict:
    '''The URLEncoded content type'''
    return {
            'application/x-www-form-urlencoded': None,
            }

# --------------------------------------------------------------------
# Create the encoders

@ioc.entity
def parameterDecoderEncoder():
    return ParameterDecoderEncoder()

# --------------------------------------------------------------------
# Creating the decoding processors
