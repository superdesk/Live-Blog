'''
Created on Jul 11, 2011

@package: Newscoop
@copyright: 2011 Sourcefabric o.p.s.
@license: http://www.gnu.org/licenses/gpl-3.0.txt
@author: Gabriel Nistor

Provides the XML encoding/decoding processor handler.
'''

from ally.internationalization import dgettext
from ally.api.operator import Model, Property
from ally.container.ioc import injected
from ally.core.impl.processor.decoder_text_base import DecodingTextBaseHandler, \
    findLastModel
from ally.core.spec.codes import BAD_CONTENT
from ally.core.spec.resources import Converter
from ally.core.spec.server import Request, Response, ProcessorsChain, \
    ContentRequest
from ally.exception import DevelException, InputException, Ref
from ally.support.api.util_type import isPropertyTypeId, isTypeIntId
from ally.xml.digester import Rule, RuleRoot, Digester, Node
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
    
    Requires on request: invoker, content, [content.contentConverter], [content.charSet]
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
        if self._isValidRequest(req):
            root = None
            
            nameModel = findLastModel(req.invoker)
            if nameModel:
                name, model = nameModel
                assert isinstance(req.content, ContentRequest)
                root = self._ruleModel(model, req.content.contentConverter or rsp.contentConverter)
                assert log.debug('Decoding model %s', model) or True
            else:
                assert log.debug('Expected a model for decoding the content, could not find one') or True
            
            if root:
                digester = Digester(root, False, False)
                try:
                    value = digester.parse(req.content.charSet or self.charSetDefault, req.content)
                    if len(digester.errors) > 0: raise InputException(*digester.errors)
                    req.arguments[name] = value
                    assert log.debug('Successfully decoded for input (%s) value %s', name, value) or True
                except DevelException as e:
                    rsp.setCode(BAD_CONTENT, e.message)
                except InputException as e:
                    rsp.setCode(BAD_CONTENT, e, 'Invalid data')
                return
        else:
            assert log.debug('Invalid request for the XML decoder') or True
        chain.proceed()
        
    def _ruleModel(self, model, converter):
        assert isinstance(model, Model)
        root = RuleRoot()
        rmodel = root.addRule(RuleModel(model), self.normalizer.normalize(model.name))
        for prop in model.properties.values():
            if isTypeIntId(prop.type) or isPropertyTypeId(prop.type):
                rmodel.addRule(RuleSetProperty(model, prop, self.converterId), \
                           self.normalizer.normalize(prop.name))
            else:
                rmodel.addRule(RuleSetProperty(model, prop, converter), \
                               self.normalizer.normalize(prop.name))
        return root

# --------------------------------------------------------------------

class RuleModel(Rule):
    '''
    Rule implementation that provides the creation of an object at begin.
    '''
    
    def __init__(self, model):
        '''
        @param model: Model
            The model to create instances for.
        '''
        assert isinstance(model, Model), 'Invalid model %s' % model
        self._model = model
        
    def begin(self, digester):
        '''
        @see: Rule.begin
        '''
        assert isinstance(digester, Digester)
        digester.stack.append(self._model.createModel())
        
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
    
    def __init__(self, model, property, converter):
        '''
        @param model: Model
            The model of the property.
        @param property: Property
            The property to be used in setting the value, this will receive as the first argument the
            last stack object and as a second the value to set.
        @param converter: Converter
            The converter to be used in transforming the content to the required value type.
        '''
        assert isinstance(model, Model), 'Invalid model %s' % model
        assert isinstance(property, Property), 'Invalid property %s' % property
        assert isinstance(converter, Converter), 'Invalid value converter %s' % converter
        self._model = model
        self._property = property
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
            self._property.set(digester.stack[-1], self._converter.asValue(content, self._property.type))
        except ValueError:
            digester.errors.append(Ref(dgettext('errors', 'Invalid value, expected %{type}s type') % 
                                    dict(type=_(str(self._property.type))), model=self._model, property=self._property))
            assert log.debug('Problems setting property %r from XML value %s', self._property.name, content) or True
