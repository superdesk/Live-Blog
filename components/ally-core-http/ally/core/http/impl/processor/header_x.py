'''
Created on Aug 9, 2011

@package: ally core http
@copyright: 2012 Sourcefabric o.p.s.
@license: http://www.gnu.org/licenses/gpl-3.0.txt
@author: Gabriel Nistor

Provides the X headers handling.
'''

from ally.api.type import formattedType, Iter
from ally.container.ioc import injected
from .header import HeaderHTTPBase, VALUES, \
    VALUE_NO_PARSE
from ally.core.http.spec import RequestHTTP, EncoderHeader, INVALID_HEADER_VALUE
from ally.core.spec.resources import Normalizer
from ally.core.spec.server import Processor, ProcessorsChain, Response, \
    ContentRequest
from ally.exception import DevelError
from ally.api.operator.type import TypeModel
from ally.api.operator.container import Model

# --------------------------------------------------------------------

@injected
class HeaderXHandler(HeaderHTTPBase, Processor, EncoderHeader):
    '''
    Provides the reading from the header of the property filters (object include) used in the response, the decoding 
    of HTTP request header 'X-Filter' for including properties in the rendering of list models. Also provides the
    encoding in the response header the included properties.
    
    Provides the reading from the header of the formating (object format) used in the response, the decoding 
    of HTTP request header 'X-Format-*' and 'X-FormatContent-*'. Also provides the encoding in the response
    header for the formating used.
    
    Provides on request: content.objFormat
    Provides on response: objInclude, objFormat
    
    Requires on request: headers, params, invoker, content
    Requires on response: NA
    '''

    normalizer = Normalizer
    # The normalizer used for matching property names with header values.
    nameXFilter = 'X-Filter'
    nameXFormat = 'X-Format-%s'
    nameXFormatContent = 'X-FormatContent-%s'

    def __init__(self):
        super().__init__()
        assert isinstance(self.normalizer, Normalizer), 'Invalid Normalizer object %s' % self.normalizer
        assert isinstance(self.nameXFilter, str), 'Invalid string %s' % self.nameXFilter
        assert isinstance(self.nameXFormat, str), 'Invalid string %s' % self.nameXFormat
        assert isinstance(self.nameXFormatContent, str), 'Invalid string %s' % self.nameXFormatContent

    def process(self, req, rsp, chain):
        '''
        @see: Processor.process
        '''
        assert isinstance(req, RequestHTTP), 'Invalid request %s' % req
        assert isinstance(chain, ProcessorsChain), 'Invalid processors chain %s' % chain
        assert isinstance(rsp, Response), 'Invalid response %s' % rsp
        assert isinstance(req.content, ContentRequest), 'Invalid content on request %s' % req.content

        try:
            p = self._parse(self.nameXFilter, req.headers, req.params, VALUES)
            if p:
                model = None
                if isinstance(req.invoker.output, Iter):
                    typ = req.invoker.output.itemType
                    if isinstance(typ, TypeModel): model = typ.container
                if model:
                    assert isinstance(model, Model)
                    for prop in model.properties:
                        try:
                            p.remove(self.normalizer.normalize(prop))
                        except ValueError: continue
                        rsp.objInclude.append(prop)
                if p:
                    rsp.setCode(INVALID_HEADER_VALUE, 'Unknown filter properties %r' % ', '.join(p))
                    return

            for clsTyp in formattedType:
                p = self._parse(self.nameXFormat % clsTyp.__name__, req.headers, req.params, VALUE_NO_PARSE)
                if p: rsp.objFormat[clsTyp] = p
                p = self._parse(self.nameXFormatContent % clsTyp.__name__, req.headers, req.params, VALUE_NO_PARSE)
                if p: req.content.objFormat[clsTyp] = p

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

        if rsp.objInclude:
            headers[self.nameXFilter] = self._encode(*[self.normalizer.normalize(prop) for prop in rsp.objInclude])

        for clsTyp, value in rsp.objFormat.items():
            headers[self.nameXFormat % clsTyp.__name__] = value
