'''
Created on Jun 18, 2011

@package: ally core
@copyright: 2011 Sourcefabric o.p.s.
@license: http://www.gnu.org/licenses/gpl-3.0.txt
@author: Gabriel Nistor

Provides the call assemblers used in constructing the resources node.
'''

from ally.api.configure import modelFor, serviceFor
from ally.api.operator import Model, Property, GET, Call, INSERT, DELETE, UPDATE, \
    Service
from ally.api.type import TypeProperty, TypeModel, Iter
from ally.container.ioc import injected
from ally.core.impl.invoker import InvokerCall, InvokerSetProperties
from ally.core.impl.node import NodeModel, NodePath, NodeProperty
from ally.core.spec.resources import Assembler, Node, Normalizer
from ally.support.api.util_type import isTypeId
from inspect import isclass
import abc
import logging
from itertools import combinations, chain

# --------------------------------------------------------------------

log = logging.getLogger(__name__)

# --------------------------------------------------------------------

class AssembleInvokers(Assembler):
    '''
    Provides support for assemblers that want to do the assembling on an invoker at one time.
    '''
        
    def assemble(self, root, invokers):
        '''
        @see: Assembler.resolve
        '''
        k = 0
        while k < len(invokers):
            if self.assembleInvoke(root, invokers[k]): del invokers[k]
            else: k += 1
    
    @abc.abstractmethod
    def assembleInvoke(self, root, invoker):
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
class AssembleGet(AssembleInvokers):
    '''
    Resolving the GET method invokers. This assembler will only accept invoker calls.
    Method signature needs to be flagged with GET and look like:
    AnyEntity|AnyEntity.Property|Iter(AnyEntity)|Iter(AnyEntity.Id)
    %
    ([...AnyEntity.Property])
    !!!Attention the order of the mandatory arguments is crucial since based on that the call is placed in the REST
    Node tree.
    '''
        
    def assembleInvoke(self, root, invoker):
        '''
        @see: AssembleInvokers.resolve
        '''
        assert isinstance(root, Node), 'Invalid node %s' % root
        assert isinstance(invoker, InvokerCall), 'Invalid invoker call %s' % invoker
        call = invoker.call
        assert isinstance(call, Call)
        if call.method != GET:
            return False
        isList = False
        typ = invoker.outputType
        if isinstance(typ, Iter):
            assert isinstance(typ, Iter)
            typ = typ.itemType
            isList = True
        try: model = typ.model
        except AttributeError:
            log.warning('Cannot extract model from output type %s for call %s', typ, call)
            return False
        
        typesMandatory = [inp.type for inp in invoker.inputs[:invoker.mandatoryCount]]
        typesExtra = [inp.type for inp in invoker.inputs[invoker.mandatoryCount:] if isinstance(inp.type, TypeProperty)]
        typesExtra = chain(*(combinations(typesExtra, k) for  k in range(0, len(typesExtra) + 1)))
        
        resolved = False
        for extra in typesExtra:
            types = list(typesMandatory)
            types.extend(extra)
            # Determine if the last path type element represents the returned model.
            if types:
                lastTyp = types[-1]
                if isinstance(lastTyp, TypeModel) or isinstance(lastTyp, TypeProperty):
                    if lastTyp.model != model:
                        types.append(model)
                else: types.append(model)
            else: types.append(model)
            
            _processHintWebName(types, call, isList)
            
            node = _obtainNode(root, types)
            if not node: continue
            
            resolved = True
            assert isinstance(node, Node)
            node.get = _processHintReplace(invoker, node.get)
            log.info('Resolved invoker %s as a get for node %s', invoker, node)
        return resolved

# --------------------------------------------------------------------

@injected
class AssembleDelete(AssembleInvokers):
    '''
    Resolving the DELETE method invokers. This assembler will only accept invoker calls.
    Method signature needs to be flagged with DELETE and look like:
    boolean
    %
    ([...AnyEntity.Property], [AnyEntity.Id])
    The last property needs to target the actual entity that is being deleted.
    !!!Attention the order of the mandatory arguments is crucial since based on that the call is placed in the REST
    Node tree.
    '''

    def assembleInvoke(self, root, invoker):
        '''
        @see: AssembleInvokers.resolve
        '''
        assert isinstance(root, Node), 'Invalid node %s' % root
        assert isinstance(invoker, InvokerCall), 'Invalid invoker call %s' % invoker
        call = invoker.call
        assert isinstance(call, Call)
        if call.method != DELETE:
            return False
        if not invoker.outputType.isOf(bool):
            log.warning('Invalid output type %s for a delete method, expected boolean', invoker.outputType)
            return False
        types = [inp.type for inp in invoker.inputs[:invoker.mandatoryCount]]
        
        _processHintWebName(types, call)
        
        node = _obtainNode(root, types)
        if not node: return False
        assert isinstance(node, Node)
        node.delete = _processHintReplace(invoker, node.delete)
        log.info('Resolved invoker %s as a delete for node %s', invoker, node)
        return True

# --------------------------------------------------------------------

@injected
class AssembleInsert(AssembleInvokers):
    '''
    Resolving the INSERT method invokers. This assembler will only accept invoker calls.
    Method signature needs to be flagged with INSERT and look like:
    TheEntity|TheEnity.Property (usually the unique id property)
    %
    ([...AnyEntity.Property], TheEntity)
    The last property needs to be of the inserted type.
    !!!Attention the order of the mandatory arguments is crucial since based on that the call is placed in the REST
    Node tree.
    '''
    
    normalizer = Normalizer
    # The normalizer used by the invoker for transforming the property names to actual references in exceptions.

    def __init__(self):
        assert isinstance(self.normalizer, Normalizer), 'Invalid Normalizer object %s' % self.normalizer
        
    def assembleInvoke(self, root, invoker):
        '''
        @see: AssembleInvokers.resolve
        '''
        assert isinstance(root, Node), 'Invalid node %s' % root
        assert isinstance(invoker, InvokerCall), 'Invalid invoker call %s' % invoker
        call = invoker.call
        assert isinstance(call, Call)
        if call.method != INSERT: return False
        types = [inp.type for inp in invoker.inputs[:invoker.mandatoryCount]]
        
        _processHintWebName(types, call)
        
        node = _obtainNode(root, types)
        if not node: return False
        assert isinstance(node, Node)
        node.insert = _processHintReplace(invoker, node.insert)
        log.info('Resolved invoker %s as a insert for node %s', invoker, node)
        return True

# --------------------------------------------------------------------

@injected  
class AssembleUpdate(AssembleInvokers):
    '''
    Resolving the UPDATE method invokers. This assembler will only accept invoker calls.
    Method signature needs to be flagged with UPDATE and look like:
    boolean
    %
    ([...AnyEntity.Property], TheEntity)
    The last property needs to be of the updated type.
    !!!Attention the order of the mandatory arguments is crucial since based on that the call is placed in the REST
    Node tree.
    '''
    
    normalizer = Normalizer
    # The normalizer used by the invoker for transforming the property names to actual references in exceptions.
    
    def __init__(self):
        assert isinstance(self.normalizer, Normalizer), 'Invalid Normalizer object %s' % self.normalizer

    def assembleInvoke(self, root, invoker):
        '''
        @see: AssembleInvokers.resolve
        '''
        assert isinstance(root, Node), 'Invalid node %s' % root
        assert isinstance(invoker, InvokerCall), 'Invalid invoker call %s' % invoker
        call = invoker.call
        assert isinstance(call, Call)
        if call.method != UPDATE:
            return False
        types = [inp.type for inp in invoker.inputs[:invoker.mandatoryCount]]
        typeModel = types[-1]
        if not isinstance(typeModel, TypeModel):
            log.info('The last input on the update is not a type model, received type %s', typeModel)
            
            _processHintWebName(types, call)

            node = _obtainNode(root, types)
            if not node: return False
            assert isinstance(node, Node)
            assert not node.update, 'There is already a update assigned for %s' % node
            node.update = invoker
            log.info('Resolved invoker %s as a update for node %s', invoker, node)
            return True
        assert isinstance(typeModel, TypeModel)
        model = typeModel.model
        assert isinstance(model, Model)
        # Removing the actual entity type since is not needed for node.
        del types[-1]
        if types:
            # Since there are types it means that the entity reference is resolved by those
            lastTyp = types[-1]
            if isinstance(lastTyp, TypeModel) or isinstance(lastTyp, TypeProperty):
                if lastTyp.model != model:
                    types.append(model)
            else: types.append(model)
            
            _processHintWebName(types, call)

            node = _obtainNode(root, types)
            if not node: return False
            assert isinstance(node, Node)
            node.update = _processHintReplace(invoker, node.update)
            log.info('Resolved invoker %s as a update for node %s', invoker, node)
            return True
        
        # If not types are present on update that means we need to try to provide a reference
        ids = []
        for prop in model.properties.values():
            assert isinstance(prop, Property)
            if isTypeId(prop.type):
                ids.append(prop)
        if not ids:
            log.warning('No property id`s found for model %s, I cannot attach to any id for updating', model)
            return False
        if len(ids) == 1:
            types.append(model.typeProperties[ids[0].name])
            
            _processHintWebName(types, call)
            
            node = _obtainNode(root, types)
            if not node: return False
            assert isinstance(node, Node)
            
            setInvoker = None
            nodeUpdate = node.update
            if nodeUpdate and isinstance(nodeUpdate, InvokerSetProperties):
                setInvoker = nodeUpdate
                nodeUpdate = setInvoker.invoker
                
            nodeUpdate = _processHintReplace(invoker, nodeUpdate)
            
            if setInvoker:
                setInvoker.invoker = nodeUpdate
                node.update = setInvoker
            else:
                node.update = InvokerSetProperties(nodeUpdate, model, [ids[0]], self.normalizer)
                
            log.info('Resolved invoker %s as a update for node %s', invoker, node)
            return True
        else:
            log.warning('To many model %s properties representing an id %s to handle', model, ids)
            return False

# --------------------------------------------------------------------

def _processHintWebName(types, call, isGroup=None):
    assert isinstance(call, Call)
    webName = call.hints.get('webName')
    if isclass(webName):
        model = modelFor(webName)
        assert isinstance(model, Model), 'Invalid web name hint class provided %s' % webName
        types.append(model)
    elif webName:
        assert isinstance(webName, str)
        webName = webName.split('/')
        for k, name in enumerate(webName):
            types.append((name, False if k <= len(webName) - 1 else isGroup))

def _processHintReplace(invoker, prevInvoker):
    if prevInvoker:
        assert isinstance(invoker, InvokerCall)
        replace = invoker.call.hints.get('replaceFor')
        if replace:
            service = serviceFor(replace)
        else:
            replace = prevInvoker.call.hints.get('replaceFor')
            assert replace, 'Cannot assemble invoker %s because already has an invoker %s and either of them has a ' \
            'replace specified' % (invoker, prevInvoker)
            prevInvoker, invoker = invoker, prevInvoker
        service = serviceFor(replace)
        assert isinstance(service, Service), \
        'Invalid replace for reference %s, cannot extract a service from it, provide a service interface' % service
        assert isinstance(prevInvoker, InvokerCall)
        assert prevInvoker.service == service, \
        'The current invoker %s does not belong to the targeted service %s, maybe you have registered the ' \
        'service in the wrong order' % (prevInvoker, service)

    return invoker
        
# --------------------------------------------------------------------

def _obtainNodePath(root, isGroup, name):
    assert isinstance(root, Node)
    for child in root.childrens():
        if isinstance(child, NodePath) and child.name == name:
            if isGroup is not None: child.isGroup |= isGroup
            return child
    return NodePath(root, False if isGroup is None else isGroup, name)

def _obtainNodeModel(root, model):
    assert isinstance(root, Node)
    for child in root.childrens():
        if isinstance(child, NodePath) and child.name == model.name:
            if isinstance(child, NodeModel): return child
            assert isinstance(child, NodePath)
            
            parent = child.parent
            if child.parent: child.parent.remChild(child)
            child.parent = None

            node = NodeModel(parent, model)
            node.get, node.insert, node.update, node.delete = child.get, child.insert, child.update, child.delete
            for c in child.childrens():
                c.parent = node
                node.addChild(c)

            return node
    return NodeModel(root, model)

def _obtainNodeProperty(root, typeProperty):
    assert isinstance(root, Node)
    for child in root.childrens():
        if isinstance(child, NodeProperty) and child.typeProperty == typeProperty:
            return child
    return NodeProperty(root, typeProperty)

# --------------------------------------------------------------------

def _obtainNode(root, types):
    node = root
    assert isinstance(node, Node)
    for typ in types:
        if isinstance(typ, TypeProperty):
            assert isinstance(typ, TypeProperty)
            addModel = True
            if isinstance(node, NodeModel) and node.model == typ.model: addModel = False
            if addModel and isinstance(node, NodeProperty) and node.typeProperty.model == typ.model:
                addModel = False
            if addModel:
                node = _obtainNodeModel(node, typ.model)
            node = _obtainNodeProperty(node, typ)
        elif isinstance(typ, TypeModel):
            assert isinstance(typ, TypeModel)
            node = _obtainNodeModel(node, typ.model)
        elif isinstance(typ, Model):
            node = _obtainNodeModel(node, typ)
        elif isinstance(typ, tuple):
            name, isGroup = typ
            node = _obtainNodePath(node, isGroup, name)
        else:
            log.warning('Unusable type %s', typ)
            return False
    return node
