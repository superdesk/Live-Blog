'''
Created on Jun 18, 2011

@package: ally core
@copyright: 2011 Sourcefabric o.p.s.
@license: http://www.gnu.org/licenses/gpl-3.0.txt
@author: Gabriel Nistor

Provides the call assemblers used in constructing the resources node.
'''

from ally.api.configure import modelFor, serviceFor, functionFor
from ally.api.model import Part
from ally.api.operator import Model, Property, GET, Call, INSERT, DELETE, UPDATE, \
    Service
from ally.api.type import TypeProperty, TypeModel, Iter, IterPart, List, Count
from ally.container.ioc import injected
from ally.core.impl.invoker import InvokerCall, InvokerSetProperties, \
    InvokerFunction
from ally.core.impl.node import NodeModel, NodePath, NodeProperty, NodeRoot
from ally.core.spec.resources import Assembler, Node, Normalizer, AssembleError
from ally.support.api.util_type import isTypeId
from inspect import isclass
from itertools import combinations, chain
import abc
import logging
import re

# --------------------------------------------------------------------

log = logging.getLogger(__name__)

# --------------------------------------------------------------------

class AssembleInvokers(Assembler):
    '''
    Provides support for assemblers that want to do the assembling on an invoker at one time.
    '''
    
    def knownModelHints(self):
        '''
        @see: AssembleInvokers.knownModelHints
        '''
        return {
                'domain': '(string) The domain where the model is registered'
                }
        
    def knownCallHints(self):
        '''
        @see: AssembleInvokers.knownCallHints
        '''
        return {
                'active': '(boolean) Flag indicating that the call is active, if a call is declared inactive no other '\
                'hints are allowed.',
                
                'webName': '(string|model API class) The name for locating the call, simply put this is the last name '\
                'used in the resource path in order to identify the call.',
                
                'replaceFor': '(service API class) Used whenever a service call has the same signature with another '\
                'service call and thus require to use the same web address, this allows to explicitly dictate what'\
                'call has priority over another call by providing the class to which the call should be replaced.',
                
                'countMethod': '(string|function) Specified the total count method for the call'
                }
        
    def assemble(self, root, invokers):
        '''
        @see: Assembler.resolve
        '''
        k = 0
        while k < len(invokers):
            invoker = invokers[k]
            assert isinstance(invoker, InvokerCall), 'Invalid invoker call %s' % invoker
            assert isinstance(invoker.call, Call)
            if invoker.call.hints.get('active', True):
                try:
                    if self.assembleInvoke(root, invoker): del invokers[k]
                    else: k += 1
                except:
                    assert isinstance(invoker, InvokerCall)
                    fnc = functionFor(invoker.service, invoker.call).__code__
                    raise AssembleError('Problems assembling call at:\nFile "%s", line %i, in %s' % \
                                        (fnc.co_filename, fnc.co_firstlineno, invoker.call.name))
            else:
                if len(invoker.call.hints) > 1:
                    fnc = functionFor(invoker.service, invoker.call).__code__
                    raise AssembleError('Illegal hints "%s" the inactive call %s:\nFile "%s", line %i, in %s' % \
                                        (','.join(name for name in invoker.call.hints.keys() if name != 'active'),
                                         invoker.call, fnc.co_filename, fnc.co_firstlineno, invoker.call.name))
                del invokers[k]
    
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
        if call.method != GET: return False
        
        typ = invoker.outputType
        if isinstance(typ, Iter):
            assert isinstance(typ, Iter)
            typ = typ.itemType
            isList = True
        else: isList = False
            
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
            
            types = processTypesHints(types, call, isList)
            
            node = obtainNode(root, types)
            if not node: continue
            
            resolved = True
            assert isinstance(node, Node)
            node.get = processInvokerHints(invoker, node.get)
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
        types = processTypesHints([inp.type for inp in invoker.inputs[:invoker.mandatoryCount]], call)
        
        node = obtainNode(root, types)
        if not node: return False
        assert isinstance(node, Node)
        node.delete = processInvokerHints(invoker, node.delete)
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
        types = processTypesHints([inp.type for inp in invoker.inputs[:invoker.mandatoryCount]], call)
        
        node = obtainNode(root, types)
        if not node: return False
        assert isinstance(node, Node)
        node.insert = processInvokerHints(invoker, node.insert)
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
            
            types = processTypesHints(types, call)

            node = obtainNode(root, types)
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
            
            types = processTypesHints(types, call)

            node = obtainNode(root, types)
            if not node: return False
            assert isinstance(node, Node)
            node.update = processInvokerHints(invoker, node.update)
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
            
            types = processTypesHints(types, call)
            
            node = obtainNode(root, types)
            if not node: return False
            assert isinstance(node, Node)
            
            setInvoker = None
            nodeUpdate = node.update
            if nodeUpdate and isinstance(nodeUpdate, InvokerSetProperties):
                setInvoker = nodeUpdate
                nodeUpdate = setInvoker.invoker
                
            nodeUpdate = processInvokerHints(invoker, nodeUpdate)
            
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

def processTypesHints(types, call, isGroup=False):
    '''
    Process the hints that affect the types used for constructing the node path.
    
    @param types: list[TypeProperty|TypeModel|Model|tuple(string,boolean)]
        The list of types to be altered based on the type hints.
    @param call: Call
        The call to process the hints for.
    @param isGroup: boolean
        Flag indicating that the hints should be considered for a group node (True) or an object node (False).
    @return: list[TypeProperty|TypeModel|Model|tuple(string,boolean)]
        The processed types.
    '''
    return processHintWebName(types, call, isGroup)

def processInvokerHints(invoker, prevInvoker):
    '''
    Process the hints that affect the invoker used on the assembled node.
    
    @param invoker: Invoker
        The invoker to be processed.
    @param prevInvoker: Invoker|None
        The previous invoker found on the node if is the case.
    @return: Invoker
        The invoker to be used.
    '''
    return processHintCountMethod(processHintReplace(invoker, prevInvoker))

# --------------------------------------------------------------------

def processHintWebName(types, call, isGroup=False):
    '''
    Processes the web name hint found on the call and alters the provided types list according to it.
    
    @param types: list[TypeProperty|TypeModel|Model|tuple(string,boolean)]
        The list of types to be altered based on the web name hint.
    @param call: Call
        The call used to extract the web name hint from.
    @param isGroup: boolean
        Flag indicating that the web name hint should be considered a group node (True) or an object node (False).
    '''
    assert isinstance(types, list), 'Invalid types %s' % types
    assert isinstance(call, Call), 'Invalid call %s' % call
    assert isinstance(isGroup, bool), 'Invalid is group flag %s' % isGroup
    
    webName = call.hints.get('webName')
    if isclass(webName):
        model = modelFor(webName)
        assert isinstance(model, Model), 'Invalid web name hint class %s for call %s' % (webName, call)
        types.append(model)
    elif webName:
        assert isinstance(webName, str), 'Invalid web name hint %s for call %s' % (webName, call)
        webName = webName.split('/')
        for k, name in enumerate(webName):
            assert re.match('^[\w]+$', name), 'Invalid name "%s" in web name "%s"' % (name, '/'.join(webName)) 
            types.append((name, False if k <= len(webName) - 1 else isGroup))
    return types

def processHintReplace(invoker, prevInvoker=None):
    '''
    Processes the replace for hint for the invokers.
    
    @param invoker: Invoker
        The invoker to be processed.
    @param prevInvoker: Invoker|None
        The previous invoker found on the node if is the case.
    @return: Invoker
        The invoker to be used.
    '''
    if prevInvoker:
        assert isinstance(invoker, InvokerCall), 'Invoker call expected %s' % invoker
        
        replace = invoker.call.hints.get('replaceFor')
        if replace:
            service = serviceFor(replace)
        else:
            assert isinstance(prevInvoker, InvokerCall), 'Invoker call expected %s' % prevInvoker
            replace = prevInvoker.call.hints.get('replaceFor')
            assert replace is not None, 'Cannot assemble invoker %s because already has an invoker %s and either ' \
                                        'of them has a replace specified' % (invoker, prevInvoker)
            prevInvoker, invoker = invoker, prevInvoker
        service = serviceFor(replace)
        assert isinstance(service, Service), 'Invalid replace for reference %s, cannot extract a service from it, '\
        'provide a service interface' % replace
            
        assert prevInvoker.service == service, 'The current invoker %s does not belong to the targeted service %s' % \
        (prevInvoker, service)

    return invoker
        
def processHintCountMethod(invoker):
    '''
    Process the hint for the count method.
    
    @param invoker: Invoker
        The invoker to be processed.
    @return: Invoker
        The invoker to be used.
    '''
    assert isinstance(invoker, InvokerCall), 'Invoker call expected %s' % invoker
    call = invoker.call
    assert isinstance(call, Call)
    
    countMethod = invoker.call.hints.get('countMethod')
    if countMethod:
        if not isinstance(countMethod, str):
            assert hasattr(countMethod, '__name__'), 'Cannot extract the count method name from %s' % countMethod
            countMethod = countMethod.__name__
        assert isinstance(invoker.service, Service)
        countCall = invoker.service.calls.get(countMethod)
        assert isinstance(countCall, Call), 'No call for name %s' % countMethod
        assert isinstance(call.outputType, Iter), 'Invalid call output type %s, expected a collection(%s) type' % \
        (call.outputType, ', '.join(Iter, List))
        assert countCall.outputType.isOf(int), 'Invalid count call output type %s, expected %s' % \
        (countCall.outputType, Count)
        
        available = set(input.name for input in countCall.inputs)
        different = available.difference(input.name for input in call.inputs)
        assert not different, 'Cannot provide values for "%s" for count method call %s' % \
        (', '.join(different), countCall)
        
        indexes = [k for k, input in enumerate(call.inputs) if input.name in available]
        def partCall(*args):
            '''
            Function that combines the call with the count call.
            '''
            countArgs = []
            for k in indexes:
                if k < len(args): countArgs.append(args[k])
                else: break
            count = countCall.call(invoker.implementation, countArgs)
            iter = call.call(invoker.implementation, args)
            return Part(iter, count)
        return InvokerFunction(IterPart(call.outputType.itemType), partCall, call.inputs, call.mandatoryCount)
        
    return invoker
    
# --------------------------------------------------------------------

def obtainNodePath(root, name, isGroup=False):
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
    
    for child in root.childrens():
        if isinstance(child, NodePath) and child.name == name:
            if isGroup is not None: child.isGroup |= isGroup
            return child
    return NodePath(root, False if isGroup is None else isGroup, name)

def obtainNodeModel(root, model):
    '''
    Obtain the model node in the provided root Node.
    
    @param root: Node
        The root node to obtain the model node in.
    @param model: Model
        The model to obtain the node for.
    @return: NodeModel
        The model node.
    '''
    assert isinstance(root, Node), 'Invalid root node %s' % root
    assert isinstance(model, Model), 'Invalid model %s' % model
    
    if isinstance(root, NodeRoot):
        domain = model.hints.get('domain')
        if domain:
            assert isinstance(domain, str) and domain, 'Invalid domain %s' % domain
            domain = domain.split('/')
            root = obtainNode(root, [(name, False) for name in domain if name.strip()])
            
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

def obtainNodeProperty(root, typeProperty):
    '''
    Obtain the property node in the provided root Node.
    
    @param root: Node
        The root node to obtain the path node in.
    @param typeProperty: TypeProperty
        The type property to find the node for.
    @return: NodeProperty
        The property node.
    '''
    assert isinstance(root, Node), 'Invalid root node %s' % root
    assert isinstance(typeProperty, TypeProperty), 'Invalid type property %s' % typeProperty

    assert isinstance(root, Node)
    for child in root.childrens():
        if isinstance(child, NodeProperty) and child.typeProperty == typeProperty:
            return child
    return NodeProperty(root, typeProperty)

def obtainNode(root, types):
    '''
    Obtains the node represented by all the provided types.
    
    @param root: Node
        The root node to obtain the node in.
    @param types: list[TypeProperty|TypeModel|Model|tuple(string,boolean)]|tuple(...)
        The list of types to identify the node.
    @return: Node|boolean
        The node for the types or False if unable to obtain one for the provided types.
    '''
    assert isinstance(root, Node), 'Invalid root node %s' % root
    assert isinstance(types, (list, tuple)), 'Invalid types %s' % types
    
    for typ in types:
        if isinstance(typ, TypeProperty):
            assert isinstance(typ, TypeProperty)
            addModel = True
            if isinstance(root, NodeModel) and root.model == typ.model: addModel = False
            if addModel and isinstance(root, NodeProperty) and root.typeProperty.model == typ.model:
                addModel = False
            if addModel:
                root = obtainNodeModel(root, typ.model)
            root = obtainNodeProperty(root, typ)
        elif isinstance(typ, TypeModel):
            assert isinstance(typ, TypeModel)
            root = obtainNodeModel(root, typ.model)
        elif isinstance(typ, Model):
            root = obtainNodeModel(root, typ)
        elif isinstance(typ, tuple):
            name, isGroup = typ
            root = obtainNodePath(root, name, isGroup)
        else:
            log.warning('Unusable type %s', typ)
            return False
    return root
