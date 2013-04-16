'''
Created on Jun 18, 2011

@package: ally core
@copyright: 2012 Sourcefabric o.p.s.
@license: http://www.gnu.org/licenses/gpl-3.0.txt
@author: Gabriel Nistor

Provides the call assemblers used in constructing the resources node.
'''

from ally.api.config import GET, DELETE, INSERT, UPDATE
from ally.api.operator.container import Model
from ally.api.operator.type import TypeService, TypeModel, TypeModelProperty
from ally.api.type import Iter, typeFor, Input
from ally.container.ioc import injected
from ally.core.impl.invoker import InvokerRestructuring
from ally.core.impl.node import NodePath, NodeProperty, NodeRoot
from ally.core.spec.resources import Node, AssembleError, Invoker, IAssembler, \
    InvokerInfo
from inspect import isclass
from itertools import combinations, chain
import abc
import logging
import re

# --------------------------------------------------------------------

log = logging.getLogger(__name__)

# --------------------------------------------------------------------

class AssembleBase(IAssembler):
    '''
    Provides support for assemblers that want to do the assembling on an invoker at one time.
    '''

    hintModelDomain = 'domain'
    hintCallWebName = 'webName'
    hintCallReplaceFor = 'replaceFor'

    def __init__(self):
        '''
        Construct the assembler.
        '''
        assert isinstance(self.hintModelDomain, str), 'Invalid hint name for model domain %s' % self.hintModelDomain
        assert isinstance(self.hintCallWebName, str), 'Invalid hint name for call web name %s' % self.hintCallWebName
        assert isinstance(self.hintCallReplaceFor, str), \
        'Invalid hint name for call replace %s' % self.hintCallReplaceFor

        self.modelHints = {
        self.hintModelDomain: '(string) The domain where the model is registered'
        }

        self.callHints = {
        self.hintCallWebName: '(string|model API class) The name for locating the call, simply put this is the last '\
        'name used in the resource path in order to identify the call.',

        self.hintCallReplaceFor: '(service API class) Used whenever a service call has the same signature with '\
        'another service call and thus require to use the same web address, this allows to explicitly dictate what'\
        'call has priority over another call by providing the class to which the call should be replaced.',
        }

    def knownModelHints(self):
        '''
        @see: IAssembler.knownModelHints
        '''
        return self.modelHints

    def knownCallHints(self):
        '''
        @see: IAssembler.knownCallHints
        '''
        return self.callHints

    # ----------------------------------------------------------------

    def processTypesHints(self, types, hints, isGroup=False):
        '''
        Process the hints that affect the types used for constructing the node path.
        
        @param types: list[Input|TypeModel|Model|tuple(string,boolean)]
            The list of types to be altered based on the type hints.
        @param hints: dictionary{string, object}
            The hints to be processed for the types.
        @param isGroup: boolean
            Flag indicating that the hints should be considered for a group node (True) or an object node (False).
        @return: list[TypeModelProperty|TypeModel|Model|tuple(string,boolean)]
            The processed types.
        '''
        return self.processHintWebName(types, hints, isGroup)

    def processInvokerHints(self, invoker, prevInvoker):
        '''
        Process the hints that affect the invoker used on the assembled node.
        
        @param invoker: Invoker
            The invoker to be processed.
        @param prevInvoker: Invoker|None
            The previous invoker found on the node if is the case.
        @return: Invoker
            The invoker to be used.
        '''
        return self.processHintReplace(invoker, prevInvoker)

    # ----------------------------------------------------------------

    def processHintWebName(self, types, hints, isGroup=False):
        '''
        Processes the web name hint found on the call and alters the provided types list according to it.
        
        @param types: list[Input|TypeModel|Model|tuple(string,boolean)]
            The list of types to be altered based on the web name hint.
        @param hints: dictionary{string, object}
            The hints to be processed for the types.
        @param isGroup: boolean
            Flag indicating that the web name hint should be considered a group node (True) or an object node (False).
        '''
        assert isinstance(types, list), 'Invalid types %s' % types
        assert isinstance(hints, dict), 'Invalid hints %s' % hints
        assert isinstance(isGroup, bool), 'Invalid is group flag %s' % isGroup

        webName = hints.get(self.hintCallWebName)
        if isclass(webName):
            typ = typeFor(webName)
            assert isinstance(typ, TypeModel), 'Invalid web name hint class %s' % webName
            types.append(typ.container)
        elif webName:
            assert isinstance(webName, str), 'Invalid web name hint %s' % webName
            webName = webName.split('/')
            for k, name in enumerate(webName):
                assert re.match('^[\w]+$', name), 'Invalid name "%s" in web name "%s"' % (name, '/'.join(webName))
                types.append((name, False if k <= len(webName) - 1 else isGroup))
        return types

    def processHintReplace(self, invoker, prevInvoker):
        '''
        Processes the replace for hint for the invokers.
        
        @param invoker: Invoker
            The invoker to be processed.
        @param prevInvoker: Invoker|None
            The previous invoker found on the node if is the case.
        @return: Invoker
            The invoker to be used.
        '''
        assert isinstance(invoker, Invoker), 'Invalid invoker %s' % invoker
        if prevInvoker:
            replace = invoker.hints.get(self.hintCallReplaceFor)
            if replace is None:
                if isinstance(prevInvoker, Invoker):
                    assert isinstance(prevInvoker, Invoker)
                    replace = prevInvoker.hints.get(self.hintCallReplaceFor)
                if replace is None:
                    raise AssembleError('Invoker %s conflicts with invoker %s and none of them has a replace specified'
                                        % (invoker, prevInvoker))
                prevInvoker, invoker = invoker, prevInvoker
            typ = typeFor(replace)
            assert isinstance(typ, TypeService), \
            'Invalid replace for reference %s, cannot extract a service from it, provide a service API' % replace

            if typeFor(prevInvoker.implementation) != typ:
                raise AssembleError('The current invoker %s does not belong to the targeted replaced service %s'
                                    % (prevInvoker, typ))

        return invoker

    # ----------------------------------------------------------------

    def isModelIn(self, model, types):
        '''
        Checks if the model is present in the provided types.
        
        @param model: Model
            The model to check if present.
        @param types: list[Input|TypeModel|Model|tuple(string,boolean)]|tuple(...)
            The types to check.
        @return: boolean
            True if the model is present, False otherwise.
        '''
        assert isinstance(model, Model), 'Invalid model %s' % model
        assert isinstance(types, (list, tuple)), 'Invalid types %s' % types
        for typ in types:
            if isinstance(typ, Input):
                assert isinstance(typ, Input)
                typ = typ.type.container

            if typ == model: return True
            elif isinstance(typ, TypeModel):
                assert isinstance(typ, TypeModel)
                if typ.container == model: return True
        return False

    # ----------------------------------------------------------------

    def obtainNodePath(self, root, name, isGroup=False):
        '''
        Obtain the path node with name in the provided root Node.
        
        @param root: Node
            The root node to obtain the path node in.
        @param name: string
            The name for the path node.
        @param isGroup: boolean
            Flag indicating that the path node should be considered a group node (True) or an object node (False).
        @return: NodePath
            The path node.
        '''
        assert isinstance(root, Node), 'Invalid root node %s' % root
        assert isinstance(name, str), 'Invalid name %s' % name
        assert isinstance(isGroup, bool), 'Invalid is group flag %s' % isGroup

        for child in root.children:
            if isinstance(child, NodePath) and child.name == name:
                if isGroup is not None: child.isGroup |= isGroup
                return child
        return NodePath(root, False if isGroup is None else isGroup, name)

    def obtainNodeModel(self, root, model):
        '''
        Obtain the model node in the provided root Node.
        
        @param root: Node
            The root node to obtain the model node in.
        @param model: Model
            The model to obtain the node for.
        @return: NodePath
            The model node.
        '''
        assert isinstance(root, Node), 'Invalid root node %s' % root
        assert isinstance(model, Model), 'Invalid model %s' % model

        if isinstance(root, NodeRoot):
            domain = model.hints.get(self.hintModelDomain)
            if domain:
                assert isinstance(domain, str) and domain, 'Invalid domain %s' % domain
                domain = domain.split('/')
                root = self.obtainNode(root, [(name, False) for name in domain if name.strip()])

        for child in root.children:
            if isinstance(child, NodePath) and child.name == model.name:
                if not child.isGroup: child.isGroup = True
                return child
        return NodePath(root, True, model.name)

    def obtainNodeProperty(self, root, inp):
        '''
        Obtain the property node in the provided root Node.
        
        @param root: Node
            The root node to obtain the path node in.
        @param inp: Input
            The input to find the node for.
        @return: NodeProperty
            The property node.
        '''
        assert isinstance(root, Node), 'Invalid root node %s' % root
        assert isinstance(inp, Input), 'Invalid input %s' % inp

        for child in root.children:
            if isinstance(child, NodeProperty) and child.isFor(inp):
                assert isinstance(child, NodeProperty)
                child.addInput(inp)
                return child
        return NodeProperty(root, inp)

    def obtainNode(self, root, types):
        '''
        Obtains the node represented by all the provided types.
        
        @param root: Node
            The root node to obtain the node in.
        @param types: list[Input|TypeModel|Model|tuple(string,boolean)]|tuple(...)
            The list of types to identify the node.
        @return: Node|boolean
            The node for the types or False if unable to obtain one for the provided types.
        '''
        assert isinstance(root, Node), 'Invalid root node %s' % root
        assert isinstance(types, (list, tuple)), 'Invalid types %s' % types

        for typ in types:
            if isinstance(typ, Input):
                assert isinstance(typ, Input)
                assert isinstance(typ.type, TypeModelProperty), 'Invalid input type %s' % typ.type
                model = typ.type.container
                assert isinstance(model, Model)

                addModel = True
                if isinstance(root, NodePath) and root.name == model.name:
                    addModel = False
                if addModel and isinstance(root, NodeProperty) and typ in root.inputs:
                    addModel = False

                if addModel: root = self.obtainNodeModel(root, model)
                root = self.obtainNodeProperty(root, typ)
            elif isinstance(typ, TypeModel):
                assert isinstance(typ, TypeModel)
                root = self.obtainNodeModel(root, typ.container)
            elif isinstance(typ, Model):
                root = self.obtainNodeModel(root, typ)
            elif isinstance(typ, tuple):
                name, isGroup = typ
                root = self.obtainNodePath(root, name, isGroup)
            else:
                log.warning('Unusable type %s', typ)
                return False
        return root

# --------------------------------------------------------------------

class AssembleOneByOne(AssembleBase):
    '''
    Provides methods for assembling the list of invokers one by one.
    @see: AssembleBase
    '''

    def assemble(self, root, invokers):
        '''
        @see: Assembler.assemble
        '''
        assert isinstance(invokers, list), 'Invalid invokers %s' % invokers
        k = 0
        while k < len(invokers):
            invoker = invokers[k]
            assert isinstance(invoker, Invoker), 'Invalid invoker %s' % invoker
            try:
                if self.assembleInvoker(root, invoker): del invokers[k]
                else: k += 1
            except:
                info = invoker.infoAPI or invoker.infoIMPL
                assert isinstance(info, InvokerInfo)
                raise AssembleError('Problems assembling invoker at:\n  File "%s", line %i, in %s' % 
                                    (info.file, info.line, info.name))

    @abc.abstractmethod
    def assembleInvoker(self, root, invoker):
        '''
        Provides the assembling for a single invoker.
        
        @param root: Node
            The root node to assemble the invokers to.
        @param invoker: Invoker
            The invoker to be assembled.
        @return: boolean
            True if the assembling has been successful, False otherwise.
        '''

# --------------------------------------------------------------------

@injected
class AssembleGet(AssembleOneByOne):
    '''
    Resolving the GET method invokers.
    Method signature needs to be flagged with GET and look like:
    AnyEntity|AnyEntity.Property|Iter(AnyEntity)|Iter(AnyEntity.Id)
    %
    ([...AnyEntity.Property])
    !!!Attention the order of the mandatory arguments is crucial since based on that the call is placed in the REST
    Node tree.
    '''

    def assembleInvoker(self, root, invoker):
        '''
        @see: AssembleOneByOne.assembleInvoker
        '''
        assert isinstance(root, Node), 'Invalid node %s' % root
        assert isinstance(invoker, Invoker), 'Invalid invoker %s' % invoker

        if invoker.method != GET: return False

        if isinstance(invoker.output, Iter):
            assert isinstance(invoker.output, Iter)
            output = invoker.output.itemType
            isList = True
        else:
            output = invoker.output
            isList = False

        if isinstance(output, (TypeModel, TypeModelProperty)):
            model = output.container
        else:
            log.info('Cannot extract model from output type %s', output)
            return False
        assert isinstance(model, Model)

        mandatory = [inp for inp in invoker.inputs[:invoker.mandatory] if isinstance(inp.type, TypeModelProperty)]
        extra = [inp for inp in invoker.inputs[invoker.mandatory:] if isinstance(inp.type, TypeModelProperty)]
        nodes = self.nodesFor(root, model, isList, mandatory, extra, invoker.hints)

        if not nodes: return False
        for node in nodes:
            assert isinstance(node, Node)
            node.get = self.processInvokerHints(invoker, node.get)
            log.info('Resolved invoker %s as a get for node %s', invoker, node)
        return True

    def nodesFor(self, root, model, isGroup, mandatory, optional, hints):
        '''
        Provides all the nodes for the provided model obtained by combining the mandatory and extra types.
        
        @param root: Node
            The root node to assemble to.
        @param model: Model
            The model to obtain the nodes for.
        @param isGroup: boolean
            Flag indicating that the model is actually provided as a collection.
        @param mandatory: list[Input]
            The mandatory inputs.
        @param optional: list[Input]
            The optional inputs.
        @param hints: dictionary{string, object}
            The hints for the invoker.
        '''
        assert isinstance(root, Node), 'Invalid node %s' % root
        assert isinstance(model, Model), 'Invalid model %s' % model
        assert isinstance(mandatory, list), 'Invalid mandatory list %s' % mandatory
        assert isinstance(optional, list), 'Invalid optional list %s' % optional
        # TODO: refactor the assembler in order to do the combinations by creating a series of invokers that will be
        # assembled separattelly
        nodes = []
        for extra in chain(*(combinations(optional, k) for k in range(0, len(optional) + 1))):
            types = list(mandatory)
            types.extend(extra)
            # Determine if the path represents the returned model.
            if not self.isModelIn(model, types): types.append(model)

            node = self.obtainNode(root, self.processTypesHints(types, hints, isGroup))
            if node: nodes.append(node)
        return nodes

# --------------------------------------------------------------------

@injected
class AssembleDelete(AssembleOneByOne):
    '''
    Resolving the DELETE method invokers.
    Method signature needs to be flagged with DELETE and look like:
    boolean
    %
    ([...AnyEntity.Property], [AnyEntity.Id])
    The last property needs to target the actual entity that is being deleted.
    !!!Attention the order of the mandatory arguments is crucial since based on that the call is placed in the REST
    Node tree.
    '''

    def assembleInvoker(self, root, invoker):
        '''
        @see: AssembleOneByOne.assembleInvoker
        '''
        assert isinstance(root, Node), 'Invalid node %s' % root
        assert isinstance(invoker, Invoker), 'Invalid invoker %s' % invoker

        if invoker.method != DELETE: return False

        if not invoker.output.isOf(bool):
            log.warning('Invalid output type %s for a delete method, expected boolean', invoker.output)
            return False

        types = [inp for inp in invoker.inputs[:invoker.mandatory] if isinstance(inp.type, TypeModelProperty)]
        if not types:
            log.info('Cannot extract any path types for %s', invoker)
            return False

        node = self.obtainNode(root, self.processTypesHints(types, invoker.hints))
        if not node: return False

        assert isinstance(node, Node)
        node.delete = self.processInvokerHints(invoker, node.delete)
        log.info('Resolved invoker %s as a delete for node %s', invoker, node)
        return True

# --------------------------------------------------------------------

@injected
class AssembleInsert(AssembleOneByOne):
    '''
    Resolving the INSERT method invokers.
    Method signature needs to be flagged with INSERT and look like:
    TheEntity|TheEnity.Property (usually the unique id property)
    %
    ([...AnyEntity.Property], [TheEntity])
    !!!Attention the order of the mandatory arguments is crucial since based on that the call is placed in the REST
    Node tree.
    '''

    def assembleInvoker(self, root, invoker):
        '''
        @see: AssembleOneByOne.assembleInvoker
        '''
        assert isinstance(root, Node), 'Invalid node %s' % root
        assert isinstance(invoker, Invoker), 'Invalid invoker %s' % invoker

        if invoker.method != INSERT: return False

        typ = invoker.output
        if isinstance(typ, (TypeModel, TypeModelProperty)):
            model = typ.container
        else:
            log.info('Cannot extract model from output type %s for invoker %s', typ, invoker)
            return False
        assert isinstance(model, Model)

        types = [inp if isinstance(inp.type, TypeModelProperty) else inp.type
                 for inp in invoker.inputs[:invoker.mandatory] if isinstance(inp.type, (TypeModelProperty, TypeModel))]

        models = [typ.container for typ in types if isinstance(typ, TypeModel)]
        if len(models) > 1:
            log.info('To many insert models %s for %s', models, invoker)
            return False

        if not self.isModelIn(model, types): types.append(model)

        node = self.obtainNode(root, self.processTypesHints(types, invoker.hints))
        if not node: return False

        assert isinstance(node, Node)
        node.insert = self.processInvokerHints(invoker, node.insert)
        log.info('Resolved invoker %s as a insert for node %s', invoker, node)
        return True

# --------------------------------------------------------------------

@injected
class AssembleUpdate(AssembleOneByOne):
    '''
    Resolving the UPDATE method invokers.
    Method signature needs to be flagged with UPDATE and look like:
    boolean
    %
    ([...AnyEntity.Property], [TheEntity])
    !!!Attention the order of the mandatory arguments is crucial since based on that the call is placed in the REST
    Node tree.
    '''

    def assembleInvoker(self, root, invoker):
        '''
        @see: AssembleOneByOne.assembleInvoker
        '''
        assert isinstance(root, Node), 'Invalid node %s' % root
        assert isinstance(invoker, Invoker), 'Invalid invoker %s' % invoker

        if invoker.method != UPDATE: return False

        types = [inp if isinstance(inp.type, TypeModelProperty) else inp.type
                 for inp in invoker.inputs[:invoker.mandatory] if isinstance(inp.type, (TypeModelProperty, TypeModel))]

        models = [typ.container for typ in types if isinstance(typ, TypeModel)]
        if len(models) > 1:
            log.info('To many update models %s for %s', models, invoker)
            return False

        node = self.obtainNode(root, self.processTypesHints(types, invoker.hints))
        if not node: return False

        assert isinstance(node, Node)
        node.update = self.processInvokerHints(invoker, node.update)
        log.info('Resolved invoker %s as a update for node %s', invoker, node)
        return True

@injected
class AssembleUpdateModel(AssembleUpdate):
    '''
    Resolving the UPDATE method invokers.
    Method signature needs to be flagged with UPDATE and look like:
    boolean
    %
    ([...AnyEntity.Property], TheEntity)
    A parameter needs to be of the updated model type.
    !!!Attention the order of the mandatory arguments is crucial since based on that the call is placed in the REST
    Node tree.
    '''

    def assembleInvoker(self, root, invoker):
        '''
        @see: AssembleOneByOne.assembleInvoker
        '''
        assert isinstance(root, Node), 'Invalid node %s' % root
        assert isinstance(invoker, Invoker), 'Invalid invoker %s' % invoker

        if invoker.method != UPDATE: return False

        types = [inp.type for inp in invoker.inputs[:invoker.mandatory] if isinstance(inp.type, TypeModelProperty)]
        modelTypes = [(inp.type, k) for k, inp in enumerate(invoker.inputs[:invoker.mandatory])
                      if isinstance(inp.type, TypeModel)]
        if len(modelTypes) == 1:
            typ, modelIndex = modelTypes[0]
            assert isinstance(typ, TypeModel)
            if typ.hasId():
                typeId = typ.propertyTypeId()
                if typeId not in types:
                    assert isinstance(typeId, TypeModelProperty)
                    inputs = list(invoker.inputs[:invoker.mandatory])
                    indexes = list(range(0, invoker.mandatory))
    
                    indexesSetValue = {modelIndex: {typeId.property:invoker.mandatory}}
    
                    inputs.append(Input('setId$%s' % typeId.property, typeId))
                    inputs.extend(invoker.inputs[invoker.mandatory:])
                    indexes.extend(range(invoker.mandatory + 1, len(inputs)))
    
                    invokerRestr = InvokerRestructuring(invoker, inputs, indexes, indexesSetValue)
                    if super().assembleInvoker(root, invokerRestr): return True
                    log.warn('Cannot assemble the exploded update invoker %s created based on invoker %s' 
                             % (invokerRestr, invoker))
        return False
