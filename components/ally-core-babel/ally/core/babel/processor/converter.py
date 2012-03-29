'''
Created on Aug 10, 2011

@package: ally core babel
@copyright: 2012 Sourcefabric o.p.s.
@license: http://www.gnu.org/licenses/gpl-3.0.txt
@author: Gabriel Nistor

Provides the converters for the response content and request content.
'''

from ally.internationalization import _
from ally.api.type import Type, Percentage, Number, Date, DateTime, Time
from ally.container.ioc import injected
from ally.core.spec.codes import INVALID_FORMATING
from ally.core.spec.resources import Converter
from ally.core.spec.server import Processor, ProcessorsChain, Request, Response, \
    Content
from ally.exception import DevelError
from babel import numbers as bn, dates as bd
from babel.core import Locale
from datetime import datetime
import logging

# --------------------------------------------------------------------

log = logging.getLogger(__name__)

# --------------------------------------------------------------------

@injected
class BabelConverterHandler(Processor):
    '''
    Implementation based on Babel for a processor that provides the converters based on language and object formating 
    for the response content and request content.
     
    Provides on request: [content.contentConverter]
    Provides on response: contentLanguage, contentConverter
    
    Requires on request: content.contentLanguage, accLanguages
    Requires on response: [contentLanguage]
    '''

    languageDefault = str
    # The default language to use when none is specified

    presentFormating = True
    # If true will present the used formatting in the response header.

    formats = {
               Date:('full', 'long', 'medium', 'short'),
               Time:('full', 'long', 'medium', 'short'),
               DateTime:('full', 'long', 'medium', 'short')
               }

    defaults = {
               Date:'medium',
               Time:'medium',
               DateTime:'medium'
               }

    def __init__(self):
        assert isinstance(self.languageDefault, str), 'Invalid string %s' % self.languageDefault

    def process(self, req, rsp, chain):
        '''
        @see: Processor.process
        '''
        assert isinstance(chain, ProcessorsChain), 'Invalid processors chain %s' % chain
        assert isinstance(req, Request), 'Invalid request %s' % req
        assert isinstance(rsp, Response), 'Invalid response %s' % rsp

        if not rsp.contentLanguage:
            for lang in req.accLanguages:
                try:
                    l = Locale.parse(lang, sep='-')
                except: continue
                rsp.contentLanguage = str(l)
                assert log.debug('Accepted language %r for response', lang) or True
                break
            else:
                rsp.contentLanguage = self.languageDefault
                assert log.debug('No language specified for the response, set default %r', rsp.contentLanguage) or True

        try:
            rsp.contentConverter = self._makeConverter(rsp, self.presentFormating)
        except DevelError as e:
            assert isinstance(e, DevelError)
            rsp.setCode(INVALID_FORMATING, 'Bad response formatting, %s' % e.message)
            return

        if req.content.contentLanguage:
            try:
                req.content.contentConverter = self._makeConverter(req.content)
            except DevelError as e:
                assert isinstance(e, DevelError)
                rsp.setCode(INVALID_FORMATING, 'Bad request content formatting, %s' % e.message)
                return
        else:
            assert log.debug('No language on the request content, cannot create converter') or True

        chain.proceed()

    def _makeConverter(self, content, presentFormating=False):
        '''
        Creates the converter for a content.
        '''
        assert isinstance(content, Content)
        l = Locale.parse(content.contentLanguage)

        formats = {}
        for clsTyp, format in content.objFormat.items():
            try:
                if clsTyp in (Number, Percentage):
                    bn.parse_pattern(format)
                elif clsTyp in self.formats:
                    if format not in self.formats[clsTyp]:
                        f = bd.parse_pattern(format)
                        print(f)
                else:
                    raise
                formats[clsTyp] = format
            except Exception as e:
                raise DevelError('invalid %s %r because: %r' % (clsTyp.__name__, format, str(e)))

        if presentFormating:
            if Number not in formats:
                content.objFormat[Number] = l.decimal_formats.get(None).pattern
            if Percentage not in formats:
                content.objFormat[Percentage] = l.percent_formats.get(None).pattern
        for clsTyp, default in self.defaults.items():
            if clsTyp not in formats:
                formats[clsTyp] = default
                if presentFormating: content.objFormat[clsTyp] = default

        return ConverterBabel(l, formats)

# --------------------------------------------------------------------

class ConverterBabel(Converter):
    '''
    Converter implementation based on Babel.
    '''

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
        raise AssertionError('Invalid object type %s for Babel converter' % objType)

    #TODO: add proper support for parsing.
    # Currently i haven't found a proper library for parsing numbers and dates, Babel has a very week support for
    # this you cannot specify the format of parsing for instance, so at this point we will use python standard.
    def asValue(self, strValue, objType):
        '''
        @see: Converter.asValue
        '''
        assert isinstance(objType, Type), 'Invalid object type %s' % objType
        if strValue is None: return None
        if objType.isOf(str):
            return strValue
        if objType.isOf(bool):
            return strValue.strip().lower() == _('true')
        if objType.isOf(Percentage):
            return float(strValue) / 100
        if objType.isOf(Number):
            if objType.isOf(int):
                return int(strValue)
            return bn.parse_decimal(strValue, self.language)
        if objType.isOf(Date):
            return datetime.strptime(strValue, '%Y-%m-%d').date()
        if objType.isOf(Time):
            return datetime.strptime(strValue, '%H:%M:%S').time()
        if objType.isOf(DateTime):
            return datetime.strptime(strValue, '%Y-%m-%d %H:%M:%S')
        raise AssertionError('Invalid object type %s for Babel converter' % objType)
