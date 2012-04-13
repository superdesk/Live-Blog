'''
Created on Jul 9, 2011

@package: ally core http
@copyright: 2012 Sourcefabric o.p.s.
@license: http://www.gnu.org/licenses/gpl-3.0.txt
@author: Gabriel Nistor

Provides the standard headers handling.
'''

from ally.api.config import GET, DELETE, INSERT, UPDATE
from ally.container.ioc import injected
from ally.core.http.spec import RequestHTTP, EncoderHeader, INVALID_HEADER_VALUE
from ally.core.spec.server import Processor, Response, ProcessorsChain, \
    ContentRequest
from ally.exception import DevelError
from ally.support.core.util_param import extractParamValues
from collections import OrderedDict
import re

# --------------------------------------------------------------------

ALL = 1
VALUE_ATTRIBUTES = 2
VALUES = 3
VALUE = 4
VALUE_NO_PARSE = 5

# --------------------------------------------------------------------

@injected
class HeaderHTTPBase:
    '''
    Provides basic methods for handling HTTP headers.
    '''

    readFromParams = False
    # If true than if the data is not present in the header will try to find it in the parameters.

    separatorMain = ','
    separatorAttr = ';'
    separatorValue = '='

    def __init__(self):
        assert isinstance(self.readFromParams, bool), 'Invalid boolean %s' % self.readFromParams
        assert isinstance(self.separatorMain, str), 'Invalid string %s' % self.separatorMain
        assert isinstance(self.separatorAttr, str), 'Invalid string %s' % self.separatorAttr
        assert isinstance(self.separatorValue, str), 'Invalid string %s' % self.separatorValue
        self._reSeparatorMain = re.compile(self.separatorMain)
        self._reSeparatorAttr = re.compile(self.separatorAttr)
        self._reSeparatorValue = re.compile(self.separatorValue)

    def _parse(self, name, headers, parameters, what=ALL):
        '''
        Parses to a dictionary the requested header name.
        
        @param name: string
            The name of the header to be parsed.
        @param headers: dictionary
            The headers to get the values from, as a key is the header name and as a value the header encoded value
            to be parsed. Attention if found the header will be removed from the provided headers dictionary.
        @param parameters: dictionary
            If the read from params flag is set to true than the header value is first checked in the provided
            parameters. Attention if header found in parameters will be removed from the provided parameters
            dictionary.
        @param what: integer
            What to be parsed, this will dictate the parsing behavior and return value.
            Can be one of ALL, VALUE_ATTRIBUTES, VALUES, VALUE.
        @return: 
            ALL: dictionary{string:dictionary{string:string}}
                A list of dictionaries containing as a key value found in the header and as the value a dictionary 
                with the values attribute. The returned dictionary is never empty, if none found this method will
                return None.
            VALUE_ATTRIBUTES: tuple(string, dictionary{string:string})
                Same like for all but will search for just one value entry and return that.
            VALUES: list[string]
                Will only parse the values ignoring the attributes.
            VALUE: string
                Provides the a single value.
        @raise DevelException: whenever the header/parameters value is not as required.
        '''
        vals = None
        if self.readFromParams:
            params = extractParamValues(parameters, name, True)
            if params:
                if what == ALL:
                    vals = OrderedDict()
                    for param in params:
                        vals.update(self.__parseValue(param, what))
                elif what == VALUES:
                    return [self.__parseValue(param, VALUE) for param in params]
                elif what in (VALUE_ATTRIBUTES, VALUE, VALUE_NO_PARSE):
                    if len(params) > 1:
                        raise DevelError('Invalid parameter header %r, expected only one value' % name)
                    if what == VALUE_NO_PARSE:
                        return params[0]
                    if what == VALUE:
                        return self.__parseValue(params[0], what)
                    return self.__parseValue(params[0], what)
                else:
                    raise AssertionError('Invalid what value %r' % what)
        header = headers.pop(name, None)
        if not vals:
            if header:
                if what == ALL:
                    vals = OrderedDict()
                    for hv in self._reSeparatorMain.split(header):
                        vals.update(self.__parseValue(hv, what))
                    return vals
                elif what == VALUES:
                    return [self.__parseValue(hv, VALUE) for hv in self._reSeparatorMain.split(header)]
                elif what in (VALUE_ATTRIBUTES, VALUE, VALUE_NO_PARSE):
                    if what == VALUE_NO_PARSE:
                        return header
                    else:
                        values = self._reSeparatorMain.split(header)
                        if len(values) > 1:
                            raise DevelError('Invalid header %r, expected only one value' % name)
                        if what == VALUE:
                            return self.__parseValue(values[0], what)
                        return self.__parseValue(values[0], what)
                else:
                    raise AssertionError('Invalid what value %r' % what)

    def _encode(self, *values):
        '''
        Encodes the provided values to a header value.
        
        @param values: arguments[tuple(string, tuple(string, string))|string]
            Tuples containing as first value found in the header and as the second value a tuple with the
            values attribute.
        @return: string
            The encoded header.
        '''
        c = []
        for v in values:
            if isinstance(v, str):
                c.append(v)
            else:
                value, attrs = v
                attrs = self.separatorValue.join(attrs)
                c.append(self.separatorAttr.join((value, attrs)) if attrs else value)

        return self.separatorMain.join(c)

    def __parseValue(self, value, what):
        '''
        INTERNAL USE ONLY.
        '''
        va = self._reSeparatorAttr.split(value)
        if what == VALUE:
            return va[0].strip()
        if len(va) > 1:
            vv = self._reSeparatorValue.split(va[1])
            attr = {vv[0].strip():vv[1] if len(vv) > 1 else None}
        else:
            attr = {}
        return va[0].strip(), attr

# --------------------------------------------------------------------

@injected
class HeaderStandardHandler(HeaderHTTPBase, Processor, EncoderHeader):
    '''
    Implementation for a processor that provides the decoding of standard HTTP request headers to actual request data 
    that can be understood by other processors. Also provides the encoding of those headers.
    
    Provides on request: [content.contentType], [content.charSet], [content.contentLanguage], [content.length],
        accContentTypes, accCharSets, accLanguages
    Provides on response: NA
    
    Requires on request: content, headers, params
    Requires on response: [contentType], [charSet], [contentLanguage], [allows], [contentLocation]
    '''

    nameContentType = 'Content-Type'
    attrContentTypeCharSet = 'charset'
    nameContentLanguage = 'Content-Language'
    nameContentLength = 'Content-Length'
    nameAllow = 'Allow'
    methodsAllow = ((GET, 'GET'), (DELETE, 'DELETE'), (INSERT, 'POST'), (UPDATE, 'PUT'))
    nameLocation = 'Location'
    nameAccept = 'Accept'
    nameAcceptCharset = 'Accept-Charset'
    nameAcceptLanguage = 'Accept-Language'

    def __init__(self):
        super().__init__()
        assert isinstance(self.nameContentType, str), 'Invalid string %s' % self.nameContentType
        assert isinstance(self.attrContentTypeCharSet, str), 'Invalid string %s' % self.attrContentTypeCharSet
        assert isinstance(self.nameContentLanguage, str), 'Invalid string %s' % self.nameContentLanguage
        assert isinstance(self.nameContentLength, str), 'Invalid string %s' % self.nameContentLength
        assert isinstance(self.nameAllow, str), 'Invalid string %s' % self.nameAllow
        assert isinstance(self.methodsAllow, tuple), 'Invalid methods allow %s' % (self.methodsAllow,)
        assert isinstance(self.nameLocation, str), 'Invalid string %s' % self.nameLocation
        assert isinstance(self.nameAccept, str), 'Invalid string %s' % self.nameAccept
        assert isinstance(self.nameAcceptCharset, str), 'Invalid string %s' % self.nameAcceptCharset
        assert isinstance(self.nameAcceptLanguage, str), 'Invalid string %s' % self.nameAcceptLanguage

    def process(self, req, rsp, chain):
        '''
        @see: Processor.process
        '''
        assert isinstance(req, RequestHTTP), 'Invalid HTTP request %s' % req
        assert isinstance(rsp, Response), 'Invalid response %s' % rsp
        assert isinstance(chain, ProcessorsChain), 'Invalid processors chain %s' % chain
        assert isinstance(req.content, ContentRequest), 'Invalid content on request %s' % req.content
        try:
            p = self._parse(self.nameContentType, req.headers, req.params, VALUE_ATTRIBUTES)
            if p:
                req.content.contentType, charset = p
                req.content.charSet = charset.get(self.attrContentTypeCharSet, req.content.charSet)

            p = self._parse(self.nameContentLanguage, req.headers, req.params, VALUE)
            if p: req.content.contentLanguage = p

            p = self._parse(self.nameContentLength, req.headers, req.params, VALUE_NO_PARSE)
            if p:
                try:
                    req.content.length = int(p)
                except ValueError:
                    rsp.setCode(INVALID_HEADER_VALUE, 'Invalid value %r for header %r' % (p, self.nameContentLength))
                    return

            p = self._parse(self.nameAccept, req.headers, req.params, VALUES)
            if p: req.accContentTypes.extend(p)

            p = self._parse(self.nameAcceptCharset, req.headers, req.params, VALUES)
            if p: req.accCharSets.extend(p)

            p = self._parse(self.nameAcceptLanguage, req.headers, req.params, VALUES)
            if p: req.accLanguages.extend(p)
        except DevelError as e:
            assert isinstance(e, DevelError)
            rsp.setCode(INVALID_HEADER_VALUE, e.message)
            return
        chain.proceed()

    def encode(self, headers, rsp):
        '''
        @see: EncoderHeader.encode
        '''
        assert isinstance(headers, dict), 'Invalid headers dictionary %s' % headers
        assert isinstance(rsp, Response), 'Invalid response %s' % rsp

        if rsp.allows != 0:
            values = [meth[1] for meth in self.methodsAllow if rsp.allows & meth[0] != 0]
            headers[self.nameAllow] = self._encode(*values)

        if rsp.contentType:
            value = rsp.contentType, (self.attrContentTypeCharSet, rsp.charSet) if rsp.charSet else ()
            headers[self.nameContentType] = self._encode(value)

        if rsp.contentLanguage: headers[self.nameContentLanguage] = rsp.contentLanguage

        if rsp.location: headers[self.nameLocation] = rsp.encoderPath.encode(rsp.location)
