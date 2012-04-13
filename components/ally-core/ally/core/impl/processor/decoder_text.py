'''
Created on Jul 11, 2011

@package: ally core
@copyright: 2011 Sourcefabric o.p.s.
@license: http://www.gnu.org/licenses/gpl-3.0.txt
@author: Gabriel Nistor

Provides the JSON encoding handler.
'''

from ally.internationalization import _
from ally.container.ioc import injected
from ally.core.impl.processor.decoder_text_base import DecodingTextBaseHandler, \
    findLastModel
from ally.core.spec.codes import BAD_CONTENT
from ally.core.spec.resources import Converter
from ally.core.spec.server import Request, Response, ProcessorsChain, \
    ContentRequest
from ally.exception import DevelError, InputError, Ref
import logging
from ally.api.config import INSERT, UPDATE
from ally.api.operator.type import TypeModel
from ally.api.operator.container import Model

# --------------------------------------------------------------------

log = logging.getLogger(__name__)

# --------------------------------------------------------------------

@injected
class DecodingTextHandler(DecodingTextBaseHandler):
    '''
    Provides the decoder for JSON content.
    
    @see: DecodingBaseHandler
        
    Provides on request: arguments
    Provides on response: NA
    
    Requires on request: method, invoker, content, content.contentType, [content.contentConverter], [content.charSet] 
    Requires on response: contentConverter
    '''

    decoder = None
    # A Callable(file, string) function used for decoding a bytes file to a text object.

    def __init__(self):
        super().__init__()
        assert callable(self.decoder), 'Invalid callable decoder %s' % self.decoder

    def process(self, req, rsp, chain):
        '''
        @see: Processor.process
        '''
        assert isinstance(req, Request), 'Invalid request %s' % req
        assert isinstance(rsp, Response), 'Invalid response %s' % rsp
        assert isinstance(chain, ProcessorsChain), 'Invalid processors chain %s' % chain
        assert req.method in (INSERT, UPDATE), 'Invalid method %s for processor' % req.method
        assert isinstance(req.content, ContentRequest), 'Invalid content on request %s' % req.content

        if req.content.contentType in self.contentTypes:
            nameModelType = findLastModel(req.invoker)

            if nameModelType:
                try:
                    obj = self.decoder(req.content, req.content.charSet or self.charSetDefault)
                except ValueError as e:
                    rsp.setCode(BAD_CONTENT, 'Invalid content  for %s' % req.content.contentType)
                    return

                name, modelType = nameModelType
                assert isinstance(req.content, ContentRequest)
                assert log.debug('Decoding model %s', modelType) or True
                try:
                    req.arguments[name] = self._decodeModel(obj, modelType,
                                                            req.content.contentConverter or rsp.contentConverter)
                    assert log.debug('Successfully decoded for input (%s) value %s', name, req.arguments[name]) or True
                except DevelError as e:
                    rsp.setCode(BAD_CONTENT, e.message)
                except InputError as e:
                    rsp.setCode(BAD_CONTENT, e, 'Invalid data')
                return
            else:
                assert log.debug('Expected a model for decoding the content, could not find one') or True
        else:
            assert log.debug('Invalid request for the text decoder') or True
        chain.proceed()

    def _decodeModel(self, modelObj, modelType, converter):
        assert isinstance(modelType, TypeModel)
        model = modelType.container
        assert isinstance(model, Model)
        assert isinstance(converter, Converter)
        mi = modelType.forClass()
        errors = []
        for prop, typ in model.properties.items():
            propName = self.normalizer.normalize(prop)
            if propName in modelObj:
                content = modelObj.pop(propName)
                if content is not None: content = content if isinstance(content, str) else str(content)
                if model.propertyId == prop: converter = self.converterId

                try: setattr(mi, prop, converter.asValue(content, typ))
                except ValueError:
                    errors.append(Ref(_('Invalid value, expected %(type)s type') %
                                      dict(type=_(str(typ))), model=model, property=prop))
                    assert log.debug('Problems setting property %r from value %s', propName, content) or True
        if len(modelObj) > 0: raise DevelError('Unknown keys %r' % ', '.join(str(key) for key in modelObj.keys()))
        if len(errors) > 0: raise DevelError(*errors)
        return mi
