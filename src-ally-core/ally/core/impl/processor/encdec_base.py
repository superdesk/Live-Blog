'''
Created on Aug 11, 2011

@package: Newscoop
@copyright: 2011 Sourcefabric o.p.s.
@license: http://www.gnu.org/licenses/gpl-3.0.txt
@author: Gabriel Nistor

Provides the basic encoding/decoding processor handler.
'''
from ally.api.operator import INSERT, UPDATE, Model, Property
from ally.api.type import Input, TypeModel
from ally.core.impl.util_type import isTypeId
from ally.core.spec.resources import Normalizer, Converter, Invoker, \
    ResourcesManager
from ally.core.spec.server import Processor, ContentRequest, Request, Response
from ally.ioc import injected
import codecs
import logging


# --------------------------------------------------------------------

log = logging.getLogger(__name__)

# --------------------------------------------------------------------

@injected
class EncodingBaseHandler(Processor):
    '''
    Provides the base encoding.
    '''
    
    resourcesManager = ResourcesManager
    # The resources manager used in locating the resource nodes for the id's presented.
    normalizer = Normalizer
    # The normalizer used by the encoding for the XML tag names.
    converterId = Converter
    # The converter to use on the id's of the models.
    charSetDefault = str
    # The default character set to be used if none provided for the content.
    contentTypes = dict
    # The dictionary[string:string] containing as a key the content types specific for this encoder and as a value
    # the content type to set on the response, if None will use the key for the content type response. 
    encodingError = str
    # The encoding error resolving.
    tagResources = 'Resources'
    # The tag to be used as the main container for the resources.
    tagListSufix = 'List'
    # Will be appended at the end of the model name when rendering the list tag containing the list items.
    attrPath = 'href'
    # The attribute name to use as the attribute in rendering the hyper link.

    def __init__(self):
        assert isinstance(self.resourcesManager, ResourcesManager), \
        'Invalid resources manager %s' % self.resourcesManager
        assert isinstance(self.normalizer, Normalizer), 'Invalid Normalizer object %s' % self.normalizer
        assert isinstance(self.converterId, Converter), 'Invalid Converter object %s' % self.converterId
        assert isinstance(self.charSetDefault, str), 'Invalid default character set %s' % self.charSetDefault
        assert isinstance(self.contentTypes, dict), 'Invalid content types %s' % self.contentTypes
        assert isinstance(self.encodingError, str), 'Invalid string %s' % self.encodingError
        assert isinstance(self.tagResources, str), 'Invalid string %s' % self.tagResources
        assert isinstance(self.tagListSufix, str), 'Invalid string %s' % self.tagListSufix
        assert isinstance(self.attrPath, str), 'Invalid string %s' % self.attrPath
        
    def _processResponse(self, rsp):
        assert isinstance(rsp, Response)
        if rsp.contentType not in self.contentTypes:
            assert log.debug('Invalid response, the content type %r is not for this %r encoder',
                             rsp.contentType, self.__class__.__name__) or True
            return False
        if not rsp.contentConverter:
            assert log.debug('Invalid response, has no content converter') or True
            return False
        contentType = self.contentTypes[rsp.contentType]
        if contentType:
            assert log.debug('Normalized content type %r to %r', rsp.contentType, contentType) or True
            rsp.contentType = contentType
        return True
    
    def _getCharSet(self, req, rsp):
        assert isinstance(req, Request)
        assert isinstance(rsp, Response)
        if rsp.charSet:
            try:
                codecs.lookup(rsp.charSet)
            except LookupError: rsp.charSet = None
        if not rsp.charSet:
            for charSet in req.accCharSets:
                try:
                    codecs.lookup(charSet)
                except LookupError: continue
                rsp.charSet = charSet
                break
        if not rsp.charSet:
            rsp.charSet = self.charSetDefault
        return rsp.charSet
    
    def _processObjectInclude(self, model, rsp):
        assert isinstance(model, Model)
        assert isinstance(rsp, Response)
        if rsp.objInclude:
            assert log.debug('There are already element in the included list') or True
        else:
            for prop in model.properties.values():
                assert isinstance(prop, Property)
                if isTypeId(prop.type):
                    rsp.objInclude.append(prop.name)
                    assert log.debug('Added the property %r to included list', prop.name) or True
                    break

# --------------------------------------------------------------------

@injected
class DecodingBaseHandler(Processor):
    '''
    Provides the base decoder for request content.
    
    Provides on request: method, content.contentType
    Provides on response: NA
    
    Requires on request: NA
    Requires on response: NA
    '''
    
    normalizer = Normalizer
    # The normalizer used by the encoding for the XML tag names.
    converterId = Converter
    # The converter to use on the id's of the models.
    charSetDefault = str
    # The default character set to be used if none provided for the content.
    contentTypes = list
    # The list[string] of content types known by this decoding.
    
    def __init__(self):
        assert isinstance(self.normalizer, Normalizer), 'Invalid Normalizer object %s' % self.normalizer
        assert isinstance(self.converterId, Converter), 'Invalid Converter object %s' % self.converterId
        assert isinstance(self.charSetDefault, str), 'Invalid default character set %s' % self.charSetDefault
        assert isinstance(self.contentTypes, list), 'Invalid content types list %s' % self.contentTypes
        
    def _isValidRequest(self, req):
        assert isinstance(req, Request)
        if req.method not in (INSERT, UPDATE): return False
        assert isinstance(req.content, ContentRequest), 'Invalid content on request %s' % req.content
        if req.content.contentType not in self.contentTypes: return False
        return True

# --------------------------------------------------------------------

def findLastModel(invoker):
    '''
    Provides if is the case the Model represented by the invoker as the last mandatory input.
    
    @param invoker: Invoker
        The invoker to find the model for.
    @return: tuple(string, Model)
        A tuple containing the name of the input and the model. None if there is no such input.
    '''
    assert isinstance(invoker, Invoker), 'Invalid invoker %s' % invoker
    if invoker.inputs:
        inp = invoker.inputs[invoker.mandatoryCount - 1]
        assert isinstance(inp, Input)
        if isinstance(inp.type, TypeModel):
            return inp.name, inp.type.model
    return None

