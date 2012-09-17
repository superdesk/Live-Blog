'''
Created on Sep 14, 2012

@package: ally core http
@copyright: 2012 Sourcefabric o.p.s.
@license: http://www.gnu.org/licenses/gpl-3.0.txt
@author: Gabriel Nistor

Provides the GMT support transformation.
'''

from ally.container.ioc import injected
from ally.core.http.spec.codes import INVALID_HEADER_VALUE
from ally.core.http.spec.server import IDecoderHeader
from ally.core.spec.codes import Code
from ally.core.spec.resources import Converter
from ally.core.spec.transform.render import Object, List
from ally.design.context import Context, requires, defines
from ally.design.processor import HandlerProcessorProceed
from datetime import datetime, date, tzinfo
from pytz import timezone, common_timezones
from pytz.exceptions import UnknownTimeZoneError

# --------------------------------------------------------------------

class Request(Context):
    '''
    The request context.
    '''
    # ---------------------------------------------------------------- Required
    decoderHeader = requires(IDecoderHeader)
    converter = requires(Converter)

class Response(Context):
    '''
    The response context.
    '''
    # ---------------------------------------------------------------- Required
    converter = requires(Converter)
    # ---------------------------------------------------------------- Defined
    code = defines(Code)
    text = defines(str)
    errorMessage = defines(str)
    errorDetails = defines(Object)

# --------------------------------------------------------------------

@injected
class TimeZoneHandler(HandlerProcessorProceed):
    '''
    Implementation for a processor that provides the time zone decoder and converter handler.
    '''

    nameTimeZone = 'X-TimeZone'
    # The header name where the time zone is set.
    nameContentTimeZone = 'X-Content-TimeZone'
    # The header name where the content time zone is set.
    baseTimeZone = 'UTC'
    # The base time zone that the server date/time values are provided.
    defaultTimeZone = 'UTC'
    # The default time zone if none is specified.

    def __init__(self):
        assert isinstance(self.nameTimeZone, str), 'Invalid time zone header name %s' % self.nameTimeZone
        assert isinstance(self.nameContentTimeZone, str), \
        'Invalid time zone content header name %s' % self.nameContentTimeZone
        assert isinstance(self.baseTimeZone, str), 'Invalid base time zone %s' % self.baseTimeZone
        assert isinstance(self.defaultTimeZone, str), 'Invalid default time zone %s' % self.defaultTimeZone
        super().__init__()

        self._baseTZ = timezone(self.baseTimeZone)
        self._defaultTZ = timezone(self.defaultTimeZone)

    def process(self, request:Request, response:Response, **keyargs):
        '''
        @see: HandlerProcessorProceed.process
        
        Provides the time zone support for the content converters.
        '''
        assert isinstance(request, Request), 'Invalid request %s' % request
        assert isinstance(response, Response), 'Invalid response %s' % response
        assert isinstance(request.decoderHeader, IDecoderHeader), 'Invalid header decoder %s' % request.decoderHeader

        failed = False
        timeZone = request.decoderHeader.retrieve(self.nameTimeZone)
        if timeZone:
            try: timeZone = timezone(timeZone)
            except UnknownTimeZoneError:
                failed = True
                response.code, response.text = INVALID_HEADER_VALUE, 'Unknown time zone'
                response.errorMessage = 'Invalid time zone \'%s\'' % timeZone

        timeZoneContent = request.decoderHeader.retrieve(self.nameContentTimeZone)
        if not failed and timeZoneContent:
            try: timeZoneContent = timezone(timeZoneContent)
            except UnknownTimeZoneError:
                failed = True
                response.code, response.text = INVALID_HEADER_VALUE, 'Unknown content time zone'
                response.errorMessage = 'Invalid content time zone \'%s\'' % timeZoneContent

        if failed:
            samples = (Object('timezone', attributes={'name', name}) for name in common_timezones)
            response.errorDetails = Object('timezone', List('sample', *samples))
            return

        if timeZone is not None:
            response.converter = ConverterTimeZone(response.converter, self._baseTZ, timeZone)
        else:
            response.converter = ConverterTimeZone(response.converter, self._baseTZ, self._defaultTZ)

        if timeZoneContent is not None:
            request.converter = ConverterTimeZone(request.converter, self._baseTZ, timeZoneContent)
        elif timeZone is not None:
            request.converter = ConverterTimeZone(request.converter, self._baseTZ, timeZone)
        else:
            request.converter = ConverterTimeZone(request.converter, self._baseTZ, self._defaultTZ)

# --------------------------------------------------------------------

class ConverterTimeZone(Converter):
    '''
    Provides the converter time zone support.
    '''
    __slots__ = ('converter', 'baseTimeZone', 'timeZone')

    def __init__(self, converter, baseTimeZone, timeZone):
        '''
        Construct the GMT converter.
        
        @param converter: Converter
            The wrapped converter.
        @param baseTimeZone: tzinfo
            The time zone of the dates to be converted.
        @param timeZone: tzinfo|None
            The time zone to convert to.
        '''
        assert isinstance(converter, Converter), 'Invalid converter %s' % converter
        assert isinstance(baseTimeZone, tzinfo), 'Invalid base time zone %s' % baseTimeZone
        assert isinstance(timeZone, tzinfo), 'Invalid time zone %s' % timeZone

        self.converter = converter
        self.baseTimeZone = baseTimeZone
        self.timeZone = timeZone

    def asValue(self, strValue, objType):
        '''
        @see: Converter.asValue
        '''
        objValue = self.converter.asValue(strValue, objType)
        if isinstance(objValue, (date, datetime)):
            objValue = self.baseTimeZone.localize(objValue)
            objValue = objValue.astimezone(self.timeZone)
            objValue = objValue.replace(tzinfo=None)
            # We need to set the time zone to None since the None TX date time generated by SQL alchemy can not be compared
            # with the date times with TZ.
        return objValue

    def asString(self, objValue, objType):
        '''
        @see: Converter.asString
        '''
        if isinstance(objValue, (date, datetime)):
            objValue = self.baseTimeZone.localize(objValue)
            objValue = objValue.astimezone(self.timeZone)
        return self.converter.asString(objValue, objType)
