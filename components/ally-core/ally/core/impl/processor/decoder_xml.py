'''
Created on Jul 11, 2011

@package: ally core
@copyright: 2011 Sourcefabric o.p.s.
@license: http://www.gnu.org/licenses/gpl-3.0.txt
@author: Gabriel Nistor

Provides the XML decoding processor handler.
'''

from ally.api.operator.container import Model
from ally.api.operator.type import TypeModel
from ally.api.type import Type
from ally.container.ioc import injected
from ally.core.impl.processor.decoder_text_base import DecodingTextBaseHandler, \
    findLastModel
from ally.core.spec.codes import BAD_CONTENT
from ally.core.spec.resources import Converter
from ally.core.spec.server import Request, Response, ProcessorsChain, \
    ContentRequest
from ally.exception import InputError, Ref
from ally.internationalization import _
from ally.xml.digester import Rule, RuleRoot, Digester, Node, DigesterError
import logging

# --------------------------------------------------------------------

log = logging.getLogger(__name__)

# --------------------------------------------------------------------

@injected
class DecodingXMLHandler(DecodingTextBaseHandler):
    '''
    Provides the decoder for XML content.
    
    @see: DecodingBaseHandler
    
    Provides on request: arguments
    Provides on response: NA
    
    Requires on request: method, invoker, content, content.contentType, [content.contentConverter], [content.charSet] 
    Requires on response: contentConverter
    '''

    def __init__(self):
        super().__init__()

    def process(self, req, rsp, chain):
        '''
        @see: Processor.process
        '''
        assert isinstance(req, Request), 'Invalid request %s' % req
        assert isinstance(rsp, Response), 'Invalid response %s' % rsp
        assert isinstance(chain, ProcessorsChain), 'Invalid processors chain %s' % chain
        content = req.content
        assert isinstance(content, ContentRequest), 'Invalid content on request %s' % content

        if content.contentType in self.contentTypes:
            root = None

            nameModelType = findLastModel(req.invoker)
            if nameModelType:
                name, modelType = nameModelType
                root = self._ruleModel(modelType, content.contentConverter)
                assert log.debug('Decoding model %s', modelType) or True
            else:
                assert log.debug('Expected a model for decoding the content, could not find one') or True

            if root:
                digester = Digester(root, False, False)
                try:
                    value = digester.parse(content.charSet, content)
                    if len(digester.errors) > 0: raise InputError(*digester.errors)
                    req.arguments[name] = value
                    assert log.debug('Successfully decoded for input (%s) value %s', name, value) or True
                except DigesterError as e:
                    rsp.setCode(BAD_CONTENT, str(e))
                except InputError as e:
                    rsp.setCode(BAD_CONTENT, e, 'Invalid data')
                return
        else:
            assert log.debug('Invalid request for the XML decoder') or True
        chain.proceed()

    def _ruleModel(self, modelType, converterValue):
        assert isinstance(modelType, TypeModel)
        model = modelType.container
        assert isinstance(model, Model)
        root = RuleRoot()
        rmodel = root.addRule(RuleModel(modelType), self.normalizer.normalize(model.name))
        for prop, typ in model.properties.items():
            if prop == model.propertyId:
                converter = self.converterId
            elif isinstance(typ, TypeModel):
                assert isinstance(typ, TypeModel)
                converter, typ = self.converterId, typ.container.properties[typ.container.propertyId]
            else:
                converter = converterValue
            rmodel.addRule(RuleSetProperty(model, prop, typ, converter), self.normalizer.normalize(prop))
        return root

# --------------------------------------------------------------------

class RuleModel(Rule):
    '''
    Rule implementation that provides the creation of an object at begin.
    '''

    def __init__(self, modelType):
        '''
        @param model: TypeModel
            The model to create instances for.
        '''
        assert isinstance(modelType, TypeModel), 'Invalid model type %s' % modelType
        self._modelType = modelType

    def begin(self, digester):
        '''
        @see: Rule.begin
        '''
        assert isinstance(digester, Digester)
        digester.stack.append(self._modelType.clazz())

    def end(self, node, digester):
        '''
        @see: Rule.end
        '''
        assert isinstance(node, Node)
        assert isinstance(digester, Digester)
        if len(digester.stack) > 1:
            digester.stack.pop()

class RuleSetProperty(Rule):
    '''
    Rule implementation that sets the content of an element to the closest stack object.
    '''

    def __init__(self, model, property, type, converter):
        '''
        @param model: Model
            The model of the property.
        @param property: string
            The property to be used in setting the value, this will receive as the first argument the
            last stack object and as a second the value to set.
        @param type: Type
            The property type.
        @param converter: Converter
            The converter to be used in transforming the content to the required value type.
        '''
        assert isinstance(model, Model), 'Invalid model %s' % model
        assert isinstance(property, str), 'Invalid property %s' % property
        assert isinstance(type, Type), 'Invalid type %s' % type
        assert isinstance(converter, Converter), 'Invalid value converter %s' % converter
        self._model = model
        self._property = property
        self._type = type
        self._converter = converter

    def begin(self, digester):
        '''
        @see: Rule.begin
        '''
        digester.stack.append(None)

    def content(self, digester, content):
        '''
        @see: Rule.content
        '''
        assert isinstance(digester, Digester)
        assert len(digester.stack) > 0, \
        'Invalid structure there is no stack object to use for setting value on path %s' % digester.currentPath()
        digester.stack[-1] = content

    def end(self, node, digester):
        '''
        @see: Rule.end
        '''
        assert isinstance(digester, Digester)
        assert len(digester.stack) > 0, \
        'Invalid structure there is no stack object to use for setting value on path %s' % digester.currentPath()
        content = digester.stack.pop()
        try:
            setattr(digester.stack[-1], self._property, self._converter.asValue(content, self._type))
        except ValueError:
            digester.errors.append(Ref(_('Invalid value, expected %(type)s type') %
                                    dict(type=_(str(self._type))), model=self._model, property=self._property))
            assert log.debug('Problems setting property %r from XML value %s', self._property, content) or True
