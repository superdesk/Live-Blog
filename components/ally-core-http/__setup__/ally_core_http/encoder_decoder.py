'''
Created on Nov 24, 2011

@package: ally core http
@copyright: 2012 Sourcefabric o.p.s.
@license: http://www.gnu.org/licenses/gpl-3.0.txt
@author: Gabriel Nistor

Provides the configurations for encoders and decoders.
'''

from ally.container import ioc

# --------------------------------------------------------------------

@ioc.config
def content_types_urlencoded() -> dict:
    '''The URLEncoded content type'''
    return {
            'application/x-www-form-urlencoded': None,
            }

# --------------------------------------------------------------------
# Creating the decoding processors
