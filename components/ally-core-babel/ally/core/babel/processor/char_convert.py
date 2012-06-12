'''
Created on Aug 10, 2011

@package: ally core babel
@copyright: 2012 Sourcefabric o.p.s.
@license: http://www.gnu.org/licenses/gpl-3.0.txt
@author: Gabriel Nistor

Provides the converters for the response content and request content.
'''

from ally.api.operator.container import Model
from ally.api.operator.type import TypeModel
from ally.api.type import Type, Percentage, Number, Date, DateTime, Time, \
    Boolean, List
from ally.container.ioc import injected
from ally.core.http.spec.extension import HTTPDecode, HTTPEncode
from ally.core.http.spec.server import IDecoderHeader, IEncoderHeader
from ally.core.spec.codes import INVALID_FORMATING
from ally.core.spec.extension import CharConvert, Language, ArgumentsAdditional, \
    LanguagesAccepted
from ally.core.spec.resources import Converter, Normalizer
from ally.core.spec.server import Response
from ally.design.processor import Handler, processor, Chain, mokup
from ally.internationalization import _
from babel import numbers as bn, dates as bd
from babel.core import Locale
from datetime import datetime
import logging

# --------------------------------------------------------------------

log = logging.getLogger(__name__)

# --------------------------------------------------------------------

FORMATTED_TYPE = (Number, Percentage, Date, Time, DateTime)
# The formatted types for the babel converter.
LIST_LOCALE = List(Locale)
# The locale list used to set as an additional argument.

class FormatError(Exception):
    '''
    Thrown for invalid formatting.
    '''
    def __init__(self, message):
        assert isinstance(message, str), 'Invalid message %s' % message
        self.message = message
        super().__init__(message)

@mokup(HTTPDecode)
class _Request(HTTPDecode, LanguagesAccepted, ArgumentsAdditional):
    ''' Used as a mokup class '''
@mokup()
class _Content(Language, CharConvert):
    ''' Used as a mokup class '''

# --------------------------------------------------------------------

@injected
class CharConvertBabelHandler(Handler):
    '''
    Implementation based on Babel for a processor that provides the converters based on language and object formating 
    for the response content and request content.
    '''

    normalizer = Normalizer
    # The normalizer to use.
    languageDefault = str
    # The default language on the response used when none is specified
    formatNameX = 'X-Format-%s'
    # The format name for the headers that specify the required format for the response content.
    formatContentNameX = 'X-FormatContent-%s'
    # The format name for the headers that specify the format for the request content.
    presentFormating = True
    # If true will present the used formatting in the response header.
    formats = {
               Date:('full', 'long', 'medium', 'short'),
               Time:('full', 'long', 'medium', 'short'),
               DateTime:('full', 'long', 'medium', 'short')
               }
    # The known keyed formats.

    defaults = {
               Date:'short',
               Time:'short',
               DateTime:'short'
               }
    # The default formats.

    def __init__(self):
        assert isinstance(self.normalizer, Normalizer), 'Invalid normalizer %s' % self.normalizer
        assert isinstance(self.languageDefault, str), 'Invalid default language %s' % self.languageDefault
        assert isinstance(self.formatNameX, str), 'Invalid name format %s' % self.formatNameX
        assert isinstance(self.formatContentNameX, str), 'Invalid name content format %s' % self.formatContentNameX
        assert isinstance(self.formats, dict), 'Invalid formats %s' % self.formats
        assert isinstance(self.defaults, dict), 'Invalid defaults %s' % self.defaults

    @processor
    def processRequestCnt(self, chain, request:HTTPDecode, requestCnt:_Content, response:Response, **keyargs):
        '''
        Provide the character conversion for request content.
        '''
        assert isinstance(chain, Chain), 'Invalid processors chain %s' % chain
        assert isinstance(request, HTTPDecode), 'Invalid request %s' % request
        assert isinstance(requestCnt, _Content), 'Invalid request content %s' % requestCnt
        assert isinstance(response, Response), 'Invalid response %s' % response
        assert isinstance(request.decoderHeader, IDecoderHeader), \
        'Invalid header decoder %s' % request.decoderHeader

        formats = {}
        for clsTyp in FORMATTED_TYPE:
            value = request.decoderHeader.retrieve(self.formatContentNameX % clsTyp.__name__)
            if value: formats[clsTyp] = value

        locale = None
        if requestCnt.language:
            try: locale = Locale.parse(requestCnt.language, sep='-')
            except: assert log.debug('Invalid request content language %s', requestCnt.language) or True

        if locale is None:
            requestCnt.language = self.languageDefault
            locale = Locale.parse(self.languageDefault)

        try: formats = self.processFormats(locale, formats)
        except FormatError as e:
            assert isinstance(e, FormatError)
            response.code, response.text = INVALID_FORMATING, 'Bad request content formatting'
            response.message = 'Bad request content formatting, %s' % e.message
            return

        requestCnt.converter = ConverterBabel(locale, formats)
        requestCnt.normalizer = self.normalizer

        chain.proceed()

    @processor
    def processResponseCnt(self, chain, request:_Request, response:Response, responseCnt:_Content, **keyargs):
        '''
        Provide the character conversion for response content.
        '''
        assert isinstance(chain, Chain), 'Invalid processors chain %s' % chain
        assert isinstance(request, HTTPDecode), 'Invalid request %s' % request
        assert isinstance(request, LanguagesAccepted), 'Invalid request %s' % request
        assert isinstance(responseCnt, _Content), 'Invalid response content %s' % responseCnt
        assert isinstance(response, Response), 'Invalid response %s' % response
        assert isinstance(request.decoderHeader, IDecoderHeader), \
        'Invalid header decoder %s' % request.decoderHeader

        formats = {}
        for clsTyp in FORMATTED_TYPE:
            value = request.decoderHeader.retrieve(self.formatNameX % clsTyp.__name__)
            if value: formats[clsTyp] = value

        locale = None
        if responseCnt.language:
            try: locale = Locale.parse(responseCnt.language, sep='-')
            except: assert log.debug('Invalid response content language %s', responseCnt.language) or True

        if locale is None:
            for lang in request.accLanguages:
                try: locale = Locale.parse(lang, sep='-')
                except:
                    assert log.debug('Invalid accepted content language %s', lang) or True
                    continue
                assert log.debug('Accepted language %s for response', locale) or True
                break
            else:
                locale = Locale.parse(self.languageDefault)
                request.accLanguages.insert(0, self.languageDefault)
                request.argumentsOfType[LIST_LOCALE] = request.accLanguages
                assert log.debug('No language specified for the response, set default %s', locale) or True

            request.argumentsOfType[Locale] = responseCnt.language = str(locale)

        try: formats = self.processFormats(locale, formats)
        except FormatError as e:
            assert isinstance(e, FormatError)
            response.code, response.text = INVALID_FORMATING, 'Bad content formatting for response'
            response.message = 'Bad content formatting for response, %s' % e.message
            return

        responseCnt.converter = ConverterBabel(locale, formats)
        responseCnt.normalizer = self.normalizer

        chain.proceed()

    @processor
    def processResponseCntHeaders(self, chain, response:HTTPEncode, responseCnt:CharConvert, **keyargs):
        '''
        Provide the response formatting header encode.
        '''
        assert isinstance(chain, Chain), 'Invalid processors chain %s' % chain
        assert isinstance(responseCnt, CharConvert), 'Invalid response content %s' % responseCnt
        assert isinstance(response, HTTPEncode), 'Invalid response %s' % response
        assert isinstance(response.encoderHeader, IEncoderHeader), \
        'Invalid response header encoder %s' % response.encoderHeader

        if isinstance(responseCnt.converter, ConverterBabel):
            assert isinstance(responseCnt.converter, ConverterBabel)
            for clsTyp, format in responseCnt.converter.formats.items():
                response.encoderHeader.encode(self.formatContentNameX % clsTyp.__name__, format)

        chain.proceed()

    # ----------------------------------------------------------------

    def processFormats(self, locale, formats):
        '''
        Process the formats to a complete list of formats that will be used by conversion.
        '''
        assert isinstance(formats, dict), 'Invalid formats %s' % formats
        assert isinstance(locale, Locale), 'Invalid locale %s' % locale

        for clsTyp, format in formats.items():
            # In here we just check that the format is valid.
            try:
                if clsTyp in (Number, Percentage): bn.parse_pattern(format)
                elif format not in self.formats[clsTyp]: bd.parse_pattern(format)
            except Exception as e:
                raise FormatError('invalid %s format \'%s\' because: %s' % (clsTyp.__name__, format, str(e)))

        if Number not in formats: formats[Number] = locale.decimal_formats.get(None).pattern
        if Percentage not in formats: formats[Percentage] = locale.percent_formats.get(None).pattern

        for clsTyp, default in self.defaults.items():
            if clsTyp not in formats: formats[clsTyp] = default

        return formats

# --------------------------------------------------------------------

class ConverterBabel(Converter):
    '''
    Converter implementation based on Babel.
    '''
    __slots__ = ('locale', 'formats')

    def __init__(self, locale, formats):
        assert isinstance(locale, Locale), 'Invalid locale %s' % locale
        assert isinstance(formats, dict), 'Invalid formats %s' % formats
        self.locale = locale
        self.formats = formats

    def asString(self, objValue, objType):
        '''
        @see: Converter.asString
        '''
        assert isinstance(objType, Type), 'Invalid object type %s' % objType
        if isinstance(objType, TypeModel): # If type model is provided we consider the model property type
            assert isinstance(objType, TypeModel)
            container = objType.container
            assert isinstance(container, Model)
            objType = container.properties[container.propertyId]
        if objType.isOf(str):
            return objValue
        if objType.isOf(bool):
            return str(objValue)
        if objType.isOf(Percentage):
            return bn.format_percent(objValue, self.formats.get(Percentage, None), self.locale)
        if objType.isOf(Number):
            return bn.format_decimal(objValue, self.formats.get(Number, None), self.locale)
        if objType.isOf(Date):
            return bd.format_date(objValue, self.formats.get(Date, None), self.locale)
        if objType.isOf(Time):
            return bd.format_time(objValue, self.formats.get(Time, None), self.locale)
        if objType.isOf(DateTime):
            return bd.format_datetime(objValue, self.formats.get(DateTime, None), None, self.locale)
        raise TypeError('Invalid object type %s for Babel converter' % objType)

    # TODO: add proper support for parsing.
    # Currently I haven't found a proper library for parsing numbers and dates, Babel has a very week support for
    # this you cannot specify the format of parsing for instance, so at this point we will use python standard.
    def asValue(self, strValue, objType):
        '''
        @see: Converter.asValue
        '''
        assert isinstance(objType, Type), 'Invalid object type %s' % objType
        if strValue is None: return None
        if isinstance(objType, TypeModel): # If type model is provided we consider the model property type 
            assert isinstance(objType, TypeModel)
            container = objType.container
            assert isinstance(container, Model)
            objType = container.properties[container.propertyId]
        if objType.isOf(str):
            return strValue
        if objType.isOf(Boolean):
            return strValue.strip().lower() == _('true').lower()
        if objType.isOf(Percentage):
            return float(strValue) / 100
        if objType.isOf(int):
            return int(strValue)
        if objType.isOf(Number):
            return bn.parse_decimal(strValue, self.locale)
        if objType.isOf(Date):
            return datetime.strptime(strValue, '%Y-%m-%d').date()
        if objType.isOf(Time):
            return datetime.strptime(strValue, '%H:%M:%S').time()
        if objType.isOf(DateTime):
            return datetime.strptime(strValue, '%Y-%m-%d %H:%M:%S')
        raise TypeError('Invalid object type %s for Babel converter' % objType)
