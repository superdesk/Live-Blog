'''
Created on Jan 23, 2012

@package: introspection request
@copyright: 2011 Sourcefabric o.p.s.
@license: http://www.gnu.org/licenses/gpl-3.0.txt
@author: Nistor Gabriel

API specifications for the node presenter.
'''

from ..api import DOMAIN
from ..api.request import IRequestService, Request, Input, Method
from ally.api.operator.container import Service, Call
from ally.api.operator.type import TypeModelProperty
from ally.container import wire
from ally.container.ioc import injected
from ally.container.proxy import proxiedClass
from ally.core.impl.invoker import InvokerCall, InvokerFunction, InvokerSetId
from ally.core.impl.node import MatchProperty
from ally.core.spec.resources import ResourcesManager, Node, Match, \
    ConverterPath
from ally.exception import InputError, Ref, DevelError
from ally.internationalization import _
from ally.support.api.util_service import trimIter
from ally.support.core.util_resources import matchesForNode, toPaths
from ally.support.util_sys import getAttrAndClass
from collections import OrderedDict
from inspect import ismodule, ismethod, getdoc
import re

# --------------------------------------------------------------------

@injected
class RequestService(IRequestService):
    '''
    Provides the implementation for @see: IRequestIntrospectService.
    '''

    resourcesManager = ResourcesManager; wire.entity('resourcesManager')
    converterPath = ConverterPath; wire.entity('converterPath')

    def __init__(self):
        '''
        Constructs the request introspect service.
        '''
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
        @see: IRequestService.getRequest
        '''
        self._refresh()
        if id not in self._requests: raise InputError(Ref(_('Invalid request id'), ref=Request.Id))
        return self._requests[id]

    def getMethod(self, id):
        '''
        @see: IRequestService.getMethod
        '''
        self._refresh()
        if id not in self._methods: raise InputError(Ref(_('Invalid method id'), ref=Method.Id))
        return self._methods[id]

    def getAllInputs(self, id, offset=None, limit=None):
        '''
        @see: IRequestService.getAllInputs
        '''
        self._refresh()
        if not id: return self._inputs.values()
        if id not in self._patternInputs: raise InputError(Ref(_('Invalid request id'), ref=Request.Id))
        return (self._inputs[inpId] for inpId in self._patternInputs[id])

    def getAllRequests(self, offset=None, limit=None):
        '''
        @see: IRequestService.getAllRequests
        '''
        self._refresh()
        values = self._requests.values()
        return trimIter(iter(values), len(values), offset, limit)

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

                patternInputs = set()

                index, inputs = 0, []
                matches = matchesForNode(node)
                for k, match in enumerate(matches):
                    assert isinstance(match, Match)
                    if not match.isValid():
                        index += 1
                        matches[k] = '{%s}' % index
                        inputs.append((match, matches[k]))

                r.Pattern = '/'.join(toPaths(matches, self.converterPath))
                if r.Pattern.startswith(DOMAIN): return

                for match, name in inputs:
                    inp = self._toPatternInput(match, r)
                    patternInputs.add(inp.Id)
                    inp.Name = name

                self._requests[r.Id] = r
                self._nodeRequests[idNode] = r.Id
                self._patternInputs[r.Id] = patternInputs
                requestMethods = self._requestMethods[r.Id] = set()

                self._requestId += 1

                if node.get:
                    m = self._toMethod(node.get, r); requestMethods.add(m.Id)
                    r.Get = m.Id
                if node.delete:
                    m = self._toMethod(node.delete, r); requestMethods.add(m.Id)
                    r.Delete = m.Id
                if node.insert:
                    m = self._toMethod(node.insert, r); requestMethods.add(m.Id)
                    r.Insert = m.Id
                if node.update:
                    m = self._toMethod(node.update, r); requestMethods.add(m.Id)
                    r.Update = m.Id

        for child in node.childrens(): self._process(child)

    def _toPatternInput(self, match, req):
        '''
        Processes the match as a pattern input.
        '''
        assert isinstance(req, Request)
        inp = Input()
        inp.Id = self._inputId
        self._inputs[self._inputId] = inp

        self._inputId += 1

        inp.Mandatory = True
        inp.ForRequest = req.Id

        if isinstance(match, MatchProperty):
            assert isinstance(match, MatchProperty)
            typ = match.type
            assert isinstance(typ, TypeModelProperty)
            inp.Description = _('The %(type)s of %(model)s %(description)s') % \
                        dict(type=_(typ.property), model=_(typ.container.name),
                        description=re.sub('[\s]+', ' ', getdoc(typ.parent.forClass) or '...'))
        else:
            raise DevelError('Unknown match %s' % match)

        return inp

    def _toMethod(self, invoker, req):
        '''
        Processes the method based on the invoker.
        '''
        assert isinstance(req, Request)
        m = Method()
        m.Id = self._methodId
        self._methods[self._methodId] = m

        m.ForRequest = req.Id

        self._methodId += 1

        if isinstance(invoker, InvokerSetId):
            assert isinstance(invoker, InvokerSetId)
            invoker = invoker.invoker

        if isinstance(invoker, InvokerCall):
            assert isinstance(invoker, InvokerCall)
            assert isinstance(invoker.service, Service)
            assert isinstance(invoker.call, Call)
            m.Name = invoker.name

            clazzApi = invoker.clazz
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
            raise DevelError('Unknown invoker %s' % invoker)

        return m
