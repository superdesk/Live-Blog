'''
Created on Nov 24, 2011

@package: ally core http
@copyright: 2012 Sourcefabric o.p.s.
@license: http://www.gnu.org/licenses/gpl-3.0.txt
@author: Gabriel Nistor

Provides the configurations for encoders and decoders.
'''

from ..ally_core.converter import contentNormalizer, converterPath
from ..ally_core.encoder_decoder import handlersDecoding, decodingNone
from .processor import headerStandard, formattingProvider
from ally.container import ioc
from ally.core.http.impl.processor.decoder_multipart import \
    DecodingMultiPartHandler
from ally.core.http.impl.url_encoded import parseStr
from ally.core.impl.processor.decoder_text import DecodingTextHandler
from ally.core.spec.server import IProcessor
from ally.core.http.impl.processor.decoder_formdata import DecodingFormDataHandler

# --------------------------------------------------------------------

@ioc.config
def content_types_urlencoded() -> dict:
    '''The URLEncoded content type'''
    return {
            'application/x-www-form-urlencoded': None,
            }

# --------------------------------------------------------------------
# Creating the decoding processors

@ioc.entity
def decoderTextUrlencoded():
    import codecs
    def decodeUrlencoded(content, charSet):
        a = parseStr(codecs.getreader(charSet)(content).read())
        return a
    return decodeUrlencoded

@ioc.entity
def decodingUrlencoded() -> IProcessor:
    b = DecodingTextHandler(); yield b
    b.normalizer = contentNormalizer()
    b.decoder = decoderTextUrlencoded()
    b.converterId = converterPath()
    b.contentTypes = list(content_types_urlencoded().keys())

@ioc.entity
def decodingFormData():
    b = DecodingFormDataHandler()
    b.contentTypeUrlEncoded = next(iter(content_types_urlencoded()))
    return b

@ioc.entity
def decodingMultipart() -> IProcessor:
    b = DecodingMultiPartHandler()
    return b

# --------------------------------------------------------------------

@ioc.entity
def encodersHeader(): return [headerStandard(), formattingProvider()]

# --------------------------------------------------------------------

@ioc.before(handlersDecoding)
def updateHandlersDecoding():
    handlersDecoding().insert(0, decodingFormData())
    handlersDecoding().insert(1, decodingMultipart())
    handlersDecoding().insert(handlersDecoding().index(decodingNone()), decodingUrlencoded())
