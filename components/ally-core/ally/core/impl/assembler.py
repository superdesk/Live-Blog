'''
Created on Jun 18, 2011

@package: ally core
@copyright: 2012 Sourcefabric o.p.s.
@license: http://www.gnu.org/licenses/gpl-3.0.txt
@author: Gabriel Nistor

Provides the call assemblers used in constructing the resources node.
'''

from ally.api.config import GET, DELETE, INSERT, UPDATE
from ally.api.model import Part, Content
from ally.api.operator.container import Call, Model
from ally.api.operator.type import TypeService, TypeModel, TypeModelProperty
from ally.api.type import Iter, IterPart, List, Count, typeFor
from ally.container.ioc import injected
from ally.core.impl.invoker import InvokerCall, InvokerSetId, InvokerFunction
from ally.core.impl.node import NodeModel, NodePath, NodeProperty, NodeRoot
from ally.core.spec.resources import Assembler, Node, Normalizer, AssembleError
from functools import partial, update_wrapper
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
                'exposed': '(boolean) Flag indicating that the call is exposed, if a call is not exposed no other ' \
                'hints are allowed. By default this flag is true whenever you decorate a call.',

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
            if invoker.call.hints.get('exposed', True):
                try:
                    if self.assembleInvoke(root, invoker): del invokers[k]
                    else: k += 1
                except:
                    raise AssembleError('Problems assembling call at:%s' % linkMessageTo(invoker))
            else:
                if len(invoker.call.hints) > 1:
                    hints = ','.join(name for name in invoker.call.hints.keys() if name != 'active')
                    raise AssembleError('Illegal hints "%s" for the unexposed call %s:%s' % (hints, invoker.call,
                                                                                             linkMessageTo(invoker)))
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

        typ = invoker.output
        if isinstance(typ, Iter):
            assert isinstance(typ, Iter)
            typ = typ.itemType
            isList = True
        else: isList = False

        if isinstance(typ, (TypeModel, TypeModelProperty)):
            model = typ.container
        else:
            log.info('Cannot extract model from output type %s for call %s', typ, call)
            return False
        assert isinstance(model, Model)

        typesMandatory, typesExtra = extractMandatoryTypes(invoker), extractOptionalTypes(invoker)
        typesExtra = chain(*(combinations(typesExtra, k) for k in range(0, len(typesExtra) + 1)))

        resolved = False
        for extra in typesExtra:
            types = list(typesMandatory)
            types.extend(extra)
            # Determine if the last path type element represents the returned model.
            if types:
                lastTyp = types[-1]
                if isinstance(lastTyp, TypeModel) or isinstance(lastTyp, TypeModelProperty):
                    if lastTyp.container != model:
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
        if not invoker.output.isOf(bool):
            log.warning('Invalid output type %s for a delete method, expected boolean', invoker.output)
            return False
        types = processTypesHints(extractMandatoryTypes(invoker), call)

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
        types = processTypesHints([inp.type for inp in invoker.inputs[:invoker.mandatory]], call)

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
        types = extractMandatoryTypes(invoker)
        lastType = types[-1]

        if isinstance(lastType, TypeModel):
            log.info('The last input on the update is type model %s', lastType)
            assert isinstance(lastType, TypeModel)
            model = lastType.container
            assert isinstance(model, Model)
            # Removing the actual entity type since is not needed for node.
            del types[-1]
            if types:
                # Since there are types it means that the entity reference is resolved by those
                lastTyp = types[-1]
                if isinstance(lastTyp, TypeModel) or isinstance(lastTyp, TypeModelProperty):
                    if lastTyp.container != model:
                        types.append(model)
                else: types.append(model)

                types = processTypesHints(types, call)

                node = obtainNode(root, types)
                if not node: return False
                assert isinstance(node, Node)
                node.update = processInvokerHints(invoker, node.update)
                log.info('Resolved invoker %s as a update for node %s', invoker, node)
                return True

            types.append(typeFor(getattr(lastType.forClass, model.propertyId)))
            types = processTypesHints(types, call)

            node = obtainNode(root, types)
            if not node: return False
            assert isinstance(node, Node)

            setInvoker = None
            nodeUpdate = node.update
            if nodeUpdate and isinstance(nodeUpdate, InvokerSetId):
                setInvoker = nodeUpdate
                nodeUpdate = setInvoker.invoker

            nodeUpdate = processInvokerHints(invoker, nodeUpdate)

            if setInvoker:
                setInvoker.invoker = nodeUpdate
                node.update = setInvoker
            else:
                node.update = InvokerSetId(nodeUpdate, self.normalizer)

            log.info('Resolved invoker %s as a update for node %s', invoker, node)
            return True

        if lastType.isOf(Content):
            log.info('The last input on the update is content %s', lastType)
            # Removing the actual entity type since is not needed for node.
            del types[-1]
            if not types:
                log.info('Cannot index content update for invoker %s, need at least one model reference', invoker)
                return False
            types = processTypesHints(types, call)

            node = obtainNode(root, types)
            if not node: return False
            assert isinstance(node, Node)
            node.update = processInvokerHints(invoker, node.update)
            log.info('Resolved invoker %s as a update for node %s', invoker, node)
            return True

        types = processTypesHints(types, call)

        node = obtainNode(root, types)
        if not node: return False
        assert isinstance(node, Node)
        assert not node.update, 'There is already a update assigned for %s' % node
        node.update = invoker
        log.info('Resolved invoker %s as a update for node %s', invoker, node)
        return True

# --------------------------------------------------------------------

def extractMandatoryTypes(invoker):
    '''
    Extracts the relevant mandatory types for the provided invoker.
    '''
    assert isinstance(invoker, InvokerCall), 'Invalid invoker call %s' % invoker
    return [inp.type for inp in invoker.inputs[:invoker.mandatory]
            if isinstance(inp.type, (TypeModel, TypeModelProperty))]

def extractOptionalTypes(invoker):
    '''
    Extracts the relevant optional types for the provided invoker.
    '''
    assert isinstance(invoker, InvokerCall), 'Invalid invoker call %s' % invoker
    return [inp.type for inp in invoker.inputs[invoker.mandatory:]
            if isinstance(inp.type, (TypeModel, TypeModelProperty))]

# --------------------------------------------------------------------

def processTypesHints(types, call, isGroup=False):
    '''
    Process the hints that affect the types used for constructing the node path.
    
    @param types: list[TypeModelProperty|TypeModel|Model|tuple(string,boolean)]
        The list of types to be altered based on the type hints.
    @param call: Call
        The call to process the hints for.
    @param isGroup: boolean
        Flag indicating that the hints should be considered for a group node (True) or an object node (False).
    @return: list[TypeModelProperty|TypeModel|Model|tuple(string,boolean)]
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
    
    @param types: list[TypeModelProperty|TypeModel|Model|tuple(string,boolean)]
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
        typ = typeFor(webName)
        assert isinstance(typ, TypeModel), 'Invalid web name hint class %s for call %s' % (webName, call)
        types.append(typ.container)
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
        if replace is None:
            if isinstance(prevInvoker, InvokerCall):
                assert isinstance(prevInvoker, InvokerCall)
                replace = prevInvoker.call.hints.get('replaceFor')
            if replace is None:
                raise AssembleError('Cannot assemble invoker %s because already has an invoker %s and either of them '
                                    'has a replace specified at:%s' % (invoker, prevInvoker, linkMessageTo(invoker)))
            prevInvoker, invoker = invoker, prevInvoker
        typ = typeFor(replace)
        assert isinstance(typ, TypeService), 'Invalid replace for reference %s, cannot extract a service from it, '\
        'provide a service API' % replace

        if typeFor(prevInvoker.implementation) != typ:
            raise AssembleError('The current invoker %s does not belong to the targeted service %s, at:%s' %
                                (prevInvoker, typ, linkMessageTo(prevInvoker)))

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

    countMethod = call.hints.get('countMethod')
    if countMethod:
        if not isinstance(countMethod, str):
            assert hasattr(countMethod, '__name__'), 'Cannot extract the count method name from %s' % countMethod
            countMethod = countMethod.__name__
        for countCall in invoker.service.calls:
            if countCall.name == countMethod: break
        else:
            raise AssembleError('No call for name %s at:%s' % (countMethod, linkMessageTo(invoker)))
        assert isinstance(countCall, Call)
        assert isinstance(call.output, Iter), 'Invalid call output type %s, expected a collection(%s) type' % \
        (call.output, ', '.join(Iter, List))
        assert countCall.output.isOf(int), 'Invalid count call output type %s, expected %s' % \
        (countCall.output, Count)

        available = set(input.name for input in countCall.inputs)
        different = available.difference(input.name for input in call.inputs)
        if different:
            raise AssembleError('Cannot provide values for "%s" for count method call %s, at:%s' %
                                (', '.join(different), countCall, linkMessageTo(countCall)))

        positions = [k for k, input in enumerate(call.inputs) if input.name in available]
        iterator = getattr(invoker.implementation, call.name)
        count = getattr(invoker.implementation, countCall.name)
        createPart = update_wrapper(partial(callCreatePart, positions, iterator, count), callCreatePart)

        return InvokerFunction(IterPart(call.output.itemType), createPart, call.inputs)

    return invoker

# --------------------------------------------------------------------

def callCreatePart(positions, iterator, count, *args):
    '''
    Function that combines the call with the count call.
    
    @param positions: list[integer]
        The list of argument positions to be passed to the count method.
    @param iterator: callable
        The callable to be called to get the iterator for the part.
    @param count: callable
        The callable that provides the total count for the part.
    @param args: arguments
        The arguments to invoke the callables with.
    @return: Part
        The part formed by invoking the iterator and count callables.
    '''
    assert isinstance(positions, (list, tuple)), 'Invalid positions %s' % positions
    assert callable(iterator), 'Invalid iterator callable %s' % iterator
    assert callable(count), 'Invalid count callable %s' % count
    countArgs = []
    for k in positions:
        if k < len(args): countArgs.append(args[k])
        else: break
    return Part(iterator(*args), count(*countArgs))

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

def obtainNodeProperty(root, type):
    '''
    Obtain the property node in the provided root Node.
    
    @param root: Node
        The root node to obtain the path node in.
    @param type: TypeModelProperty
        The type property to find the node for.
    @return: NodeProperty
        The property node.
    '''
    assert isinstance(root, Node), 'Invalid root node %s' % root
    assert isinstance(type, TypeModelProperty), 'Invalid type property %s' % type

    assert isinstance(root, Node)
    for child in root.childrens():
        if isinstance(child, NodeProperty) and child.type == type:
            return child
    return NodeProperty(root, type)

def obtainNode(root, types):
    '''
    Obtains the node represented by all the provided types.
    
    @param root: Node
        The root node to obtain the node in.
    @param types: list[TypeModelProperty|TypeModel|Model|tuple(string,boolean)]|tuple(...)
        The list of types to identify the node.
    @return: Node|boolean
        The node for the types or False if unable to obtain one for the provided types.
    '''
    assert isinstance(root, Node), 'Invalid root node %s' % root
    assert isinstance(types, (list, tuple)), 'Invalid types %s' % types

    for typ in types:
        if isinstance(typ, TypeModelProperty):
            assert isinstance(typ, TypeModelProperty)
            addModel = True
            if isinstance(root, NodeModel) and root.model == typ.container: addModel = False
            if addModel and isinstance(root, NodeProperty) and root.model == typ.container:
                addModel = False
            if addModel:
                root = obtainNodeModel(root, typ.container)
            root = obtainNodeProperty(root, typ)
        elif isinstance(typ, TypeModel):
            assert isinstance(typ, TypeModel)
            root = obtainNodeModel(root, typ.container)
        elif isinstance(typ, Model):
            root = obtainNodeModel(root, typ)
        elif isinstance(typ, tuple):
            name, isGroup = typ
            root = obtainNodePath(root, name, isGroup)
        else:
            log.warning('Unusable type %s', typ)
            return False
    return root

# --------------------------------------------------------------------

def linkMessageTo(invoker):
    '''
    Provides a link message to the provided invoker call. The idea is to provide a message that is recoginzed by the IDE
    and allow you to use CTRL_click to go to the problem invoker call function.
    
    @param invoker: InvokerCall
        The invoker call to generate the message for.
    @return: string
        The message that will link the call API function.
    '''
    assert isinstance(invoker, InvokerCall), 'Invalid invoker %s' % invoker
    fnc = getattr(invoker.clazz, invoker.call.name).__code__
    return '\nFile "%s", line %i, in %s' % (fnc.co_filename, fnc.co_firstlineno, invoker.call.name)
