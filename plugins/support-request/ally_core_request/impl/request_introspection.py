'''
Created on Jan 23, 2012

@package ally core request
@copyright 2011 Sourcefabric o.p.s.
@license http://www.gnu.org/licenses/gpl-3.0.txt
@author: Gabriel Nistor

API specifications for the node presenter.
'''

from ..api.request_introspection import IRequestIntrospectService
from ally import internationalization
from ally.api.operator import Property, Model, Call, Service
from ally.api.type import TypeProperty
from ally.container import wire
from ally.container.ioc import injected
from ally.container.proxy import proxiedClass
from ally.core.impl.invoker import InvokerCall, InvokerFunction, \
    InvokerSetProperties
from ally.core.impl.node import MatchProperty
from ally.core.spec.resources import ResourcesManager, Node, Match, \
    ConverterPath
from ally.exception import InputException, Ref, DevelException
from ally.support.core.util_resources import matchesForNode, toPaths
from ally.support.util_sys import getAttrAndClass
from ally_core_request.api.request_introspection import Request, Input, Method
from collections import OrderedDict
from inspect import ismodule, ismethod, getdoc
import re

# --------------------------------------------------------------------

_ = internationalization.translator(__name__)

# --------------------------------------------------------------------

@injected
class RequestIntrospectService(IRequestIntrospectService):
    '''
    Provides the implementation for @see: IRequestIntrospectService.
    '''
    
    resourcesManager = ResourcesManager; wire.entity('resourcesManager')
    converterPath = ConverterPath; wire.entity('converterPath')
    
    def __init__(self):
        wire.validateWiring(self)
        self._requestId = 1
        self._inputId = 1
        self._methodId = 1
        
        self._nodeRequests = {}
        self._requests = OrderedDict()
        self._patternInputs = {}
        self._inputs = OrderedDict()
        self._requestMethods = {}
        self._methods = OrderedDict()
        
    def getRequest(self, id):
        '''
        @see: IRequestIntrospectService.getRequest
        '''
        self._refresh()
        if id not in self._requests: raise InputException(Ref(_('Invalid request id'), ref=Request.Id))
        return self._requests[id]
    
    def getMethod(self, id):
        '''
        @see: IRequestIntrospectService.getMethod
        '''
        self._refresh()
        if id not in self._methods: raise InputException(Ref(_('Invalid method id'), ref=Method.Id))
        return self._methods[id]
    
    def getAllInputs(self, id):
        '''
        @see: IRequestIntrospectService.getAllInputs
        '''
        self._refresh()
        if not id: return self._inputs.values()
        if id not in self._patternInputs: raise InputException(Ref(_('Invalid request id'), ref=Request.Id))
        return (self._inputs[inpId] for inpId in self._patternInputs[id]) 
    
    def getAllRequests(self, offset, limit):
        '''
        @see: IRequestIntrospectService.getAllRequests
        '''
        self._refresh()
        return self._requests.values()
    
    # ----------------------------------------------------------------
    
    def _refresh(self):
        '''
        Refreshes the requests.
        '''
        self._process(self.resourcesManager.getRoot())
        
    def _process(self, node):
        '''
        Processes the node and sub nodes requests.
        '''
        assert isinstance(node, Node), 'Invalid root node %s' % node
        if node.get or node.delete or node.insert or node.update:
            idNode = id(node)
            if idNode not in self._nodeRequests:
                r = Request()
                r.Id = self._requestId
                self._requests[r.Id] = r
                self._nodeRequests[idNode] = r.Id
                patternInputs = self._patternInputs[r.Id] = set()
                requestMethods = self._requestMethods[r.Id] = set()
                
                self._requestId += 1

                index = 0
                matches = matchesForNode(node)
                for k, match in enumerate(matches):
                    assert isinstance(match, Match)
                    if not match.isValid():
                        inp = self._toPatternInput(match)
                        patternInputs.add(inp.Id)

                        index += 1
                        matches[k] = inp.Name = '{%s}' % index
                        
                r.Pattern = '/'.join(toPaths(matches, self.converterPath))
                
                if node.get:
                    m = self._toMethod(node.get); requestMethods.add(m.Id)
                    r.Get = m.Id
                if node.delete:
                    m = self._toMethod(node.delete); requestMethods.add(m.Id)
                    r.Delete = m.Id
                if node.insert:
                    m = self._toMethod(node.insert); requestMethods.add(m.Id)
                    r.Insert = m.Id
                if node.update:
                    m = self._toMethod(node.update); requestMethods.add(m.Id)
                    r.Update = m.Id
                
        for child in node.childrens(): self._process(child)
    
    def _toPatternInput(self, match):
        '''
        Processes the match as a pattern input.
        '''
        inp = Input()
        inp.Id = self._inputId
        self._inputs[self._inputId] = inp
        
        self._inputId += 1

        inp.Mandatory = True
        
        if isinstance(match, MatchProperty):
            assert isinstance(match, MatchProperty)
            typProp = match.typeProperty
            assert isinstance(typProp, TypeProperty)
            assert isinstance(typProp.property, Property)
            assert isinstance(typProp.model, Model)
            inp.Description = _('The $1 of $2($3)', _(typProp.property.name), _(typProp.model.name),
                                _(re.sub('[\s]+', ' ', (getdoc(typProp.model.modelClass) or '...'))))
        else:
            raise DevelException('Unknown match %s' % match)
            
        return inp
    
    def _toMethod(self, invoker):
        '''
        Processes the method based on the invoker.
        '''
        m = Method()
        m.Id = self._methodId
        self._methods[self._methodId] = m
        
        self._methodId += 1
        
        if isinstance(invoker, InvokerSetProperties):
            assert isinstance(invoker, InvokerSetProperties)
            invoker = invoker.invoker
        
        if isinstance(invoker, InvokerCall):
            assert isinstance(invoker, InvokerCall)
            assert isinstance(invoker.service, Service)
            assert isinstance(invoker.call, Call)
            m.Name = invoker.name
            
            clazzApi = invoker.service.serviceClass
            methodApi, clazzApiDef = getAttrAndClass(clazzApi, invoker.name)
            m.APIDoc = getdoc(methodApi)
            m.APIClass = clazzApi.__module__ + '.' + clazzApi.__name__
            m.APIClassDefiner = clazzApiDef.__module__ + '.' + clazzApiDef.__name__
            
            if ismodule(invoker.implementation):
                m.IMPL = invoker.implementation.__name__
                m.IMPLDoc = getdoc(getattr(invoker.implementation, invoker.call.name))
            else: 
                clazzImpl = proxiedClass(invoker.implementation.__class__)
                methodImpl, clazzImplDef = getAttrAndClass(clazzImpl, invoker.name)
                m.IMPLDoc = getdoc(methodImpl)
                m.IMPL = clazzImpl.__module__ + '.' + clazzImpl.__name__
                m.IMPLDefiner = clazzImplDef.__module__ + '.' + clazzImplDef.__name__
        elif isinstance(invoker, InvokerFunction):
            assert isinstance(invoker, InvokerFunction)
            m.Name = invoker.name
            
            if ismethod(invoker.function):
                clazzImpl = proxiedClass(invoker.function.__self__.__class__)
                methodImpl, clazzImplDef = getAttrAndClass(clazzImpl, invoker.name)
                m.IMPLDoc = getdoc(methodImpl)
                m.IMPL = clazzImpl.__module__ + '.' + clazzImpl.__name__
                m.IMPLDefiner = clazzImplDef.__module__ + '.' + clazzImplDef.__name__
            else:
                m.IMPL = invoker.function.__module__
                m.IMPLDoc = getdoc(invoker.function)
                m.IMPLDefiner = invoker.function.__module__
        else:
            raise DevelException('Unknown invoker %s' % invoker)
            
        return m
