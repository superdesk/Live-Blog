'''
Created on Jul 11, 2011

@package: Newscoop
@copyright: 2011 Sourcefabric o.p.s.
@license: http://www.gnu.org/licenses/gpl-3.0.txt
@author: Gabriel Nistor

Provides the JSON encoding handler.
'''

from ally.internationalization import _
from ally.api.operator import Model, Property, INSERT, UPDATE
from ally.container.ioc import injected
from ally.core.impl.processor.decoder_text_base import DecodingTextBaseHandler, \
    findLastModel
from ally.core.spec.codes import BAD_CONTENT
from ally.core.spec.resources import Converter
from ally.core.spec.server import Request, Response, ProcessorsChain, \
    ContentRequest
from ally.exception import DevelException, InputException, Ref
from ally.support.api.util_type import isPropertyTypeId, isTypeIntId
import logging

# --------------------------------------------------------------------

log = logging.getLogger(__name__)

# --------------------------------------------------------------------

@injected
class DecodingTextHandler(DecodingTextBaseHandler):
    '''
    Provides the decoder for JSON content.
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
        if self._isValidRequest(req):
            nameModel = findLastModel(req.invoker)
            
            if nameModel:
                try:
                    obj = self.decoder(req.content, req.content.charSet or self.charSetDefault)
                except ValueError as e:
                    rsp.setCode(BAD_CONTENT, 'Invalid JSON content')
                    return

                name, model = nameModel
                assert isinstance(req.content, ContentRequest)
                assert log.debug('Decoding model %s', model) or True
                try:
                    req.arguments[name] = self._decodeModel(obj, model,
                                                            req.content.contentConverter or rsp.contentConverter)
                    assert log.debug('Successfully decoded for input (%s) value %s', name, req.arguments[name]) or True
                except DevelException as e:
                    rsp.setCode(BAD_CONTENT, e.message)
                except InputException as e:
                    rsp.setCode(BAD_CONTENT, e, 'Invalid data')
                return
            else:
                assert log.debug('Expected a model for decoding the content, could not find one') or True
        else:
            assert log.debug('Invalid request for the JSON decoder') or True
        chain.proceed()
            
    def _decodeModel(self, obj, model, converter):
        assert isinstance(model, Model)
        assert isinstance(converter, Converter)
        objCount = 1
        modelName = self.normalizer.normalize(model.name)
        modelObj = obj.pop(modelName, None)
        if modelObj is None:
            raise DevelException('Expected key %r for object count %s' % (modelName, objCount))
        if len(obj) > 0:
            raise DevelException('Unknown keys %r for object count %s' % 
                                   (', '.join(str(key) for key in obj.keys()), objCount))
        objCount += 1
        obj = modelObj
        mi = model.createModel()
        errors = []
        for prop in model.properties.values():
            assert isinstance(prop, Property)
            propName = self.normalizer.normalize(prop.name)
            if propName in obj:
                content = obj.pop(propName)
                if content is not None: content = content if isinstance(content, str) else str(content)
                if isTypeIntId(prop.type) or isPropertyTypeId(prop.type):
                    converter = self.converterId
                try:
                    prop.set(mi, converter.asValue(content, prop.type))
                except ValueError:
                    errors.append(Ref(_('Invalid value, expected %(type)s type') % 
                                      dict(type=_(str(prop.type))), model=model, property=prop))
                    assert log.debug('Problems setting property %r from JSON value %s', propName, content) or True
        if len(obj) > 0: raise DevelException('Unknown keys %r' % ', '.join(str(key) for key in obj.keys()))
        if len(errors) > 0: raise InputException(*errors)
        return mi
