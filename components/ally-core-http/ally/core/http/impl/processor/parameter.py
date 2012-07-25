'''
Created on May 25, 2012

@package: ally core http
@copyright: 2011 Sourcefabric o.p.s.
@license: http://www.gnu.org/licenses/gpl-3.0.txt
@author: Gabriel Nistor

Provides the parameters handler.
'''

from ally.api.criteria import AsOrdered
from ally.api.operator.container import Criteria, Query
from ally.api.operator.type import TypeQuery, TypeCriteriaEntry, TypeCriteria
from ally.api.type import Input, Type, Iter, typeFor
from ally.container.ioc import injected
from ally.core.spec.codes import ILLEGAL_PARAM, Code
from ally.core.spec.transform.render import Object, List
from ally.core.spec.transform.support import obtainOnDict, setterOnDict, \
    getterChain, getterOnObj, setterOnObj, setterWithGetter, obtainOnObj, \
    getterOnDict, getterOnObjIfIn, SAMPLE
from ally.core.spec.resources import Invoker, Path, Node, INodeInvokerListener, \
    Normalizer, Converter
from ally.design.context import Context, requires, defines
from ally.design.processor import HandlerProcessorProceed
from collections import deque, Iterable, OrderedDict
from weakref import WeakKeyDictionary
import logging
import random
import re

# --------------------------------------------------------------------

log = logging.getLogger(__name__)

# --------------------------------------------------------------------

class Request(Context):
    '''
    The request context.
    '''
    # ---------------------------------------------------------------- Required
    parameters = requires(list)
    path = requires(Path)
    invoker = requires(Invoker)
    arguments = requires(dict)
    converterParameters = requires(Converter)
    normalizerParameters = requires(Normalizer)

class Response(Context):
    '''
    The response context.
    '''
    # ---------------------------------------------------------------- Defined
    code = defines(Code)
    text = defines(str)
    errorMessage = defines(str)
    errorDetails = defines(Object)

# --------------------------------------------------------------------

@injected
class ParameterHandler(HandlerProcessorProceed, INodeInvokerListener):
    '''
    Implementation for a processor that provides the transformation of parameters into arguments.
    '''

    separatorName = '.'
    # The separator used for parameter names.
    nameOrderAsc = 'asc'
    # The name used for the ascending list of names.
    nameOrderDesc = 'desc'
    # The name used for the descending list of names.
    regexSplitValues = '[\s]*(?<!\\\)\,[\s]*'
    # The regex used for splitting list values.
    separatorValue = ','
    # The separator used for the list values.
    regexNormalizeValue = '\\\(?=\,)'
    # The regex used for normalizing the split values.
    separatorValueEscape = '\,'
    # The separator escape used for list values.

    def __init__(self):
        assert isinstance(self.separatorName, str), 'Invalid separator for names %s' % self.separatorName
        assert isinstance(self.nameOrderAsc, str), 'Invalid name for ascending %s' % self.nameOrderAsc
        assert isinstance(self.nameOrderDesc, str), 'Invalid name for descending %s' % self.nameOrderDesc
        assert isinstance(self.regexSplitValues, str), 'Invalid regex for values split %s' % self.regexSplitValues
        assert isinstance(self.separatorValue, str), 'Invalid separator for values %s' % self.separatorValue
        assert isinstance(self.regexNormalizeValue, str), \
        'Invalid regex for value normalize %s' % self.regexNormalizeValue
        assert isinstance(self.separatorValueEscape, str), \
        'Invalid separator escape for values %s' % self.separatorValueEscape
        HandlerProcessorProceed.__init__(self)

        self._reSplitValues = re.compile(self.regexSplitValues)
        self._reNormalizeValue = re.compile(self.regexNormalizeValue)
        self._cacheDecode = WeakKeyDictionary()
        self._cacheEncode = WeakKeyDictionary()

    def process(self, request:Request, response:Response, **keyargs):
        '''
        @see: HandlerProcessorProceed.process
        
        Process the parameters into arguments.
        '''
        assert isinstance(request, Request), 'Invalid request %s' % request
        assert isinstance(response, Response), 'Invalid response %s' % response
        if Response.code in response and not response.code.isSuccess: return # Skip in case the response is in error

        assert isinstance(request.path, Path), 'Invalid request %s has no resource path' % request
        assert isinstance(request.path.node, Node), 'Invalid resource path %s has no node' % request.path
        invoker = request.invoker
        assert isinstance(invoker, Invoker), 'No invoker available for %s' % request

        if request.parameters:
            decode = self._cacheDecode.get(invoker)
            if decode is None:
                decode = self.decodeInvoker(invoker)
                request.path.node.addNodeListener(self)
                self._cacheDecode[invoker] = decode

            illegal = []
            context = dict(target=request.arguments,
                           normalizer=request.normalizerParameters, converter=request.converterParameters)
            for name, value in request.parameters:
                if not decode(path=name, value=value, **context): illegal.append((name, value))

            if illegal:
                encode = self._cacheEncode.get(invoker)
                if encode is None:
                    encode = self.encodeInvoker(invoker)
                    request.path.node.addNodeListener(self)
                    self._cacheEncode[invoker] = encode

                response.code, response.text = ILLEGAL_PARAM, 'Illegal parameter'
                context = dict(normalizer=request.normalizerParameters, converter=request.converterParameters)
                sample = encode(value=SAMPLE, **context)

                errors = [List('illegal', *(Object('parameter', attributes={'name':name}) for name, _value in illegal))]
                if sample:
                    assert isinstance(sample, deque), 'Invalid sample %s' % sample

                    response.errorMessage = 'Illegal parameter or value'
                    samples = (Object('parameter', attributes=OrderedDict((('name', name), ('expected', value))))
                               for name, value in sample)
                    errors.append(List('sample', *samples))
                else:
                    response.errorMessage = 'No parameters are allowed on this URL'
                response.errorDetails = Object('parameter', *errors)

    # ----------------------------------------------------------------

    def onInvokerChange(self, node, old, new):
        '''
        @see: INodeInvokerListener.onInvokerChange
        '''
        self._cacheDecode.pop(old, None)
        self._cacheEncode.pop(old, None)

    # ----------------------------------------------------------------

    def decodePrimitive(self, setter, typeValue):
        '''
        Create a decode exploit for a primitive value.
        
        @param setter: callable(object, object)
            The setter used to set the value to the target object.
        @param typeValue: Type
            The type of the value to decode.
        @return: callable(**data) -> boolean
            The exploit that provides the primitive decoding.
        '''
        assert callable(setter), 'Invalid setter %s' % setter
        assert isinstance(typeValue, Type), 'Invalid type %s' % typeValue

        def exploit(path, target, value, converter, **data):
            assert isinstance(path, deque), 'Invalid path %s' % path
            assert isinstance(converter, Converter), 'Invalid converter %s' % converter

            if path: return False
            # Only if there are no other elements in path we process the exploit
            if not isinstance(value, str): return False
            # If the value is not a string then is not valid
            try: value = converter.asValue(value, typeValue)
            except ValueError: return False
            setter(target, value)
            return True

        return exploit

    def decodePrimitiveList(self, setter, typeItem):
        '''
        Exploit to decode a primitive value list.
        
        @param setter: callable(object, object)
            The setter used to set the value to the target object.
        @param typeItem: Type
            The type represented by the list items.
        @return: callable(**data) -> boolean
            The exploit that provides the primitive list decoding.
        '''
        assert callable(setter), 'Invalid setter %s' % setter
        assert isinstance(typeItem, Type), 'Invalid type %s' % typeItem

        def exploit(path, target, value, converter, **data):
            assert isinstance(path, deque), 'Invalid path %s' % path
            assert isinstance(converter, Converter), 'Invalid converter %s' % converter

            if path: return False
            # Only if there are no other elements in path we process the exploit
            if not isinstance(value, str): return False
            # If the value is not a string then is not valid
            if isinstance(value, str):
                value = self._reSplitValues.split(value)
                for k in range(0, len(value)): value[k] = self._reNormalizeValue.sub('', value[k])

            if not isinstance(value, (list, tuple)): value = (value,)

            for item in value:
                try: item = converter.asValue(item, typeItem)
                except ValueError: return False
                setter(target, item)
            return True

        return exploit

    def decodePath(self, children):
        '''
        Exploit to locate a decoder in the provided children based on the exploit path.
        
        @param children: dictionary{string, callable(**data)}
            The children exploits to be identified based on the key.
        @return: callable(**data) -> boolean
            The exploit that provides the path decoding.
        '''
        assert isinstance(children, dict), 'Invalid children %s' % children
        if __debug__:
            for keyChild, exploitChild in children.items():
                assert isinstance(keyChild, str), 'Invalid child key %s' % keyChild
                assert callable(exploitChild), 'Invalid child exploit %s' % exploitChild

        def exploit(path, normalizer, **data):
            assert isinstance(path, deque), 'Invalid path %s' % path
            assert path, 'Invalid path, needs to have at least one entry'
            assert isinstance(normalizer, Normalizer), 'Invalid normalizer %s' % normalizer

            key = path.popleft()
            if not isinstance(key, str): return False
            assert isinstance(key, str), 'Invalid path element %s' % key

            for keyChild, exploitChild in children.items():
                assert isinstance(keyChild, str), 'Invalid child key %s' % keyChild
                if normalizer.normalize(keyChild) == key: break
            else: return False
            return exploitChild(path=path, normalizer=normalizer, **data)

        return exploit

    def decodeCriteria(self, typeCriteria, getterCriteria):
        '''
        Exploit that provides the decoder for the criteria.
        
        @param typeCriteria: TypeCriteria
            The criteria type to decode.
        @param getterCriteria: callable(object) -> object
            The getter used to get the criteria from the target object.
        @return: callable(**data) -> boolean
            The exploit that provides the criteria decoding.
        '''
        assert isinstance(typeCriteria, TypeCriteria), 'Invalid criteria type %s' % typeCriteria
        assert callable(getterCriteria), 'Invalid getter %s' % getterCriteria
        criteria = typeCriteria.container
        assert isinstance(criteria, Criteria)

        if issubclass(typeCriteria.clazz, AsOrdered): exclude = ('ascending', 'priority')
        else: exclude = ()

        children = {}
        for prop, typeProp in criteria.properties.items():
            if prop in exclude: continue

            if isinstance(typeProp, Iter):
                assert isinstance(typeProp, Iter)

                setter = setterWithGetter(obtainOnObj(prop, list), list.append)
                propDecode = self.decodePrimitiveList(setter, typeProp.itemType)
            else: propDecode = self.decodePrimitive(setterOnObj(prop), typeProp)
            children[prop] = propDecode

        exploitPath = self.decodePath(children)
        def exploit(path, target, **data):
            assert isinstance(path, deque), 'Invalid path %s' % path

            if path: return exploitPath(path=path, target=getterCriteria(target), **data)
            if not criteria.main: return False

            data.update(path=path, target=getterCriteria(target))
            for prop in criteria.main:
                if not children[prop](**data): return False
            return True

        return exploit

    def decodeSetOrder(self, typeEntry, getterQuery):
        '''
        Create a decode exploit that sets the orderer.
        
        @param typeEntry: TypeCriteriaEntry
            The criteria entry type to set the order for.
        @param getterQuery: callable(object) -> object
            The getter used to get the query from the target object.
        @return: callable(**data) -> boolean
            The exploit that sets the ordering.
        '''
        assert isinstance(typeEntry, TypeCriteriaEntry), 'Invalid entry type %s' % typeEntry
        assert callable(getterQuery), 'Invalid getter %s' % getterQuery
        assert isinstance(typeEntry.parent, TypeQuery)

        def exploit(path, target, value, **data):
            assert isinstance(path, deque), 'Invalid path %s' % path
            if path: return False
            # Only if there are no other elements in path we process the exploit
            query = getterQuery(target)
            assert typeEntry.parent.isValid(query), 'Invalid query object %s' % query
            # We first find the biggest priority in the query
            priority = 0
            for etype in typeEntry.parent.childTypes():
                assert isinstance(etype, TypeCriteriaEntry)
                if etype == typeEntry: continue
                if not etype.isOf(AsOrdered): continue

                if etype in query:
                    criteria = getattr(query, etype.name)
                    assert isinstance(criteria, AsOrdered), 'Invalid criteria %s' % criteria
                    if AsOrdered.priority in criteria: priority = max(priority, criteria.priority)

            criteria = getattr(query, typeEntry.name)
            assert isinstance(criteria, AsOrdered), 'Invalid criteria %s' % criteria
            criteria.ascending = value
            criteria.priority = priority + 1
            return True

        return exploit

    def decodeOrder(self, ascending, exploitOrder):
        '''
        Exploit to decode the order. Basically this exploit converts the ascending and descending parameter values to
        paths that are processed by the provided children.
        
        @param ascending: boolean
            The value used for this order.
        @param exploitOrder: callable(**data) -> boolean
            The exploit to be used in the order decoding.
        @return: callable(**data) -> boolean
            The exploit that provides the ordering decoding.
        '''
        assert isinstance(ascending, bool), 'Invalid ascending flag %s' % ascending
        assert callable(exploitOrder), 'Invalid order exploit %s' % exploitOrder

        def exploit(path, value, **data):
            assert isinstance(path, deque), 'Invalid path %s' % path
            if path: return False
            # Only if there are no other elements in path we process the exploit
            if isinstance(value, (list, tuple)): values = value
            else: values = (value,)

            data.update(value=ascending)
            for value in values:
                if not isinstance(value, str): return False
                else:
                    paths = self._reSplitValues.split(value)
                    for k in range(0, len(paths)): paths[k] = self._reNormalizeValue.sub('', paths[k])
                    for path in paths:
                        data.update(path=deque(path.split(self.separatorName)))
                        if not exploitOrder(**data): return False
            return True

        return exploit

    def decodeInvoker(self, invoker):
        '''
        Create a decode exploit for the invoker.
        
        @param invoker: Invoker
            The invoker to create a parameters decoder for.
        @return: callable(**data) -> boolean
            The exploit that provides the invoker decoding.
        '''
        assert isinstance(invoker, Invoker), 'Invalid invoker %s' % invoker

        children, ordered = {}, {}
        for inp in invoker.inputs:
            assert isinstance(inp, Input)
            typeInp = inp.type
            assert isinstance(typeInp, Type)

            if typeInp.isPrimitive:
                if isinstance(typeInp, Iter):
                    assert isinstance(typeInp, Iter)

                    setter = setterWithGetter(obtainOnDict(inp.name, list), list.append)
                    inpDecode = self.decodePrimitiveList(setter, typeInp.itemType)
                else: inpDecode = self.decodePrimitive(setterOnDict(inp.name), typeInp)
                children[inp.name] = inpDecode

            elif isinstance(typeInp, TypeQuery):
                assert isinstance(typeInp, TypeQuery)
                assert isinstance(typeInp.query, Query)

                childrenQuery, orderedQuery, getterQuery = {}, {}, obtainOnDict(inp.name, inp.type.clazz)
                for nameEntry, classCriteria in typeInp.query.criterias.items():

                    getter = getterChain(getterQuery, getterOnObj(nameEntry))
                    childrenQuery[nameEntry] = self.decodeCriteria(typeFor(classCriteria), getter)

                    if issubclass(classCriteria, AsOrdered):
                        orderedQuery[nameEntry] = self.decodeSetOrder(typeInp.childTypeFor(nameEntry), getterQuery)

                isUpdated = False
                if invoker.output.isOf(typeInp.owner):
                    # If the query is a main query and also there is no name conflict then add the query children to
                    # the main children
                    if set(childrenQuery.keys()).isdisjoint(children.keys()) and set(orderedQuery).isdisjoint(ordered):
                        isUpdated = True
                        children.update(childrenQuery)
                        ordered.update(orderedQuery)

                if not isUpdated:
                    children[inp.name] = self.decodePath(childrenQuery)
                    ordered[inp.name] = self.decodePath(orderedQuery)

        if self.nameOrderAsc in children: log.error('Name conflict for \'%s\' in %s', self.nameOrderAsc, invoker)
        elif self.nameOrderDesc in children: log.error('Name conflict for \'%s\' in %s', self.nameOrderDesc, invoker)
        else:
            exploitOrder = self.decodePath(ordered)
            children[self.nameOrderAsc] = self.decodeOrder(True, exploitOrder)
            children[self.nameOrderDesc] = self.decodeOrder(False, exploitOrder)

        exploitPath = self.decodePath(children)
        def exploit(path, **data):
            assert isinstance(path, str), 'Invalid path %s' % path

            path = deque(path.split(self.separatorName))
            return exploitPath(path=path, **data)

        return exploit

    # ----------------------------------------------------------------

    def encodePrimitive(self, typeValue, getterValue):
        '''
        Create a encode exploit for a primitive value also encodes primitive value list.
        
        @param typeValue: Type
            The type of the value to encode.
        @param getterValue: callable(object) -> object
            The getter used to get the value from the value object.
        @return: callable(**data)
            The exploit that provides the primitive encoding.
        '''
        assert isinstance(typeValue, Type), 'Invalid type %s' % typeValue
        assert callable(getterValue), 'Invalid getter %s' % getterValue

        def exploit(path, value, target, converter, **data):
            assert isinstance(path, str), 'Invalid path %s' % path
            assert isinstance(target, deque), 'Invalid target %s' % target
            assert isinstance(converter, Converter), 'Invalid converter %s' % converter

            if value is SAMPLE:
                if isinstance(typeValue, Iter):
                    assert isinstance(typeValue, Iter)
                    target.append((path, 'a %s collection' % typeValue.itemType))
                else:
                    target.append((path, 'a %s value' % typeValue))
            else:
                value = getterValue(value)
                if value is None: return
                if isinstance(typeValue, Iter):
                    assert isinstance(value, Iterable), 'Invalid value %s' % value
                    value = [converter.asString(item, typeValue.itemType) for item in value]
                    value = [item.replace(self.separatorValue, self.separatorValueEscape) for item in value]
                    value = self.separatorValue.join(value)
                else:
                    value = converter.asString(value, typeValue)
                target.append((path, value))

        return exploit

    def encodePath(self, children):
        '''
        Exploit to encode the path of the exploits by using the children keys.
        
        @param children: dictionary{string, callable(**data)}
            The children exploits to be identified based on the key.
        @return: callable(**data)
            The exploit that provides the path encoding.
        '''
        assert isinstance(children, dict), 'Invalid children %s' % children
        if __debug__:
            for keyChild, exploitChild in children.items():
                assert isinstance(keyChild, str), 'Invalid child key %s' % keyChild
                assert callable(exploitChild), 'Invalid child exploit %s' % exploitChild

        def exploit(normalizer, path='', **data):
            assert isinstance(path, str), 'Invalid path %s' % path
            assert isinstance(normalizer, Normalizer), 'Invalid normalizer %s' % normalizer

            data.update(normalizer=normalizer)
            for keyChild, exploitChild in children.items():
                assert isinstance(keyChild, str), 'Invalid child key %s' % keyChild

                pathChild = normalizer.normalize(keyChild)
                if path: pathChild = self.separatorName.join((path, pathChild))

                exploitChild(path=pathChild, **data)

        return exploit

    def encodeCriteria(self, typeCriteria, getterCriteria):
        '''
        Exploit that provides the encoding for the criteria.
        
        @param typeCriteria: TypeCriteria
            The criteria type to encode.
        @param getterCriteria: callable(object) -> object
            The getter used to get the criteria from the value object.
        @return: callable(**data)
            The exploit that provides the criteria encoding.
        '''
        assert isinstance(typeCriteria, TypeCriteria), 'Invalid criteria type %s' % typeCriteria
        assert callable(getterCriteria), 'Invalid getter %s' % getterCriteria
        criteria = typeCriteria.container
        assert isinstance(criteria, Criteria)

        if issubclass(typeCriteria.clazz, AsOrdered): exclude = ('ascending', 'priority')
        else: exclude = ()

        children, childrenMain = OrderedDict(), OrderedDict()
        for prop, typeProp in sorted(criteria.properties.items(), key=lambda item: item[0]):
            if prop in exclude: continue
            propEncode = self.encodePrimitive(typeProp, getterOnObjIfIn(prop, typeCriteria.childTypeFor(prop)))
            if prop in criteria.main: childrenMain[prop] = propEncode
            else: children[prop] = propEncode

        exploitPath = self.encodePath(children) if children else None
        exploitPathMain = self.encodePath(childrenMain) if childrenMain else None
        def exploit(value, target, path='', **data):
            assert isinstance(path, str), 'Invalid path %s' % path
            assert isinstance(target, deque), 'Invalid target %s' % target

            if value is not SAMPLE:
                value = getterCriteria(value)
                if value is None: return
            data.update(path=path, value=value)
            if exploitPathMain:
                targetMain = deque()
                exploitPathMain(target=targetMain, **data)
                if targetMain:
                    targetMainIter = iter(targetMain)
                    _name, valueMain = next(targetMainIter)
                    for _name, val in targetMainIter:
                        if valueMain != val:
                            target.extend(targetMain)
                            break
                    else: target.append((path, valueMain))
            if exploitPath: exploitPath(target=target, **data)

        return exploit

    def encodeGetOrder(self, typeEntry, getterQuery):
        '''
        Create a encode exploit that gets the orderer.
        
        @param typeEntry: TypeCriteriaEntry
            The criteria entry type to get the order for.
        @param getterQuery: callable(object) -> object
            The getter used to get the query from the value object.
        @return: callable(**data)
            The exploit that gets the ordering.
        '''
        assert isinstance(typeEntry, TypeCriteriaEntry), 'Invalid entry type %s' % typeEntry
        assert callable(getterQuery), 'Invalid getter %s' % getterQuery
        assert isinstance(typeEntry.parent, TypeQuery)

        def exploit(path, value, target, **data):
            assert isinstance(path, str), 'Invalid path %s' % path
            assert isinstance(target, deque), 'Invalid target %s' % target

            if value is SAMPLE:
                target.append((path, random.choice((True, False)), random.randint(0, 10)))
            else:
                query = getterQuery(value)
                if query is None: return
                assert typeEntry.parent.isValid(query), 'Invalid query object %s' % query

                if typeEntry in query:
                    criteria = getattr(query, typeEntry.name)
                    assert isinstance(criteria, AsOrdered), 'Invalid criteria %s' % criteria
                    if AsOrdered.ascending in criteria:
                        target.append((path, criteria.ascending, criteria.priority))

        return exploit

    def encodeOrder(self, exploitOrder):
        '''
        Exploit to encode the order.
        
        @param exploitOrder: callable(**data) -> boolean
            The exploit to be used in getting the order values.
        @return: callable(**data) -> boolean
            The exploit that provides the ordering encode.
        '''
        assert callable(exploitOrder), 'Invalid order exploit %s' % exploitOrder

        def exploit(target, normalizer, **data):
            assert isinstance(target, deque), 'Invalid target %s' % target
            assert isinstance(normalizer, Normalizer), 'Invalid normalizer %s' % normalizer

            targetOrdering = deque()
            exploitOrder(target=targetOrdering, normalizer=normalizer, **data)
            if targetOrdering:
                ordering, priortized = [], []
                for order in targetOrdering:
                    path, asscending, priority = order
                    if asscending is None: continue
                    if priority is None: ordering.append((path, asscending))
                    else: priortized.append(order)

                priortized.sort(key=lambda order: not order[1]) # Order by asc/desc
                priortized.sort(key=lambda order: order[2]) # Order by priority

                ordering.sort(key=lambda order: not order[1]) # Order by asc/desc
                priortized.extend(ordering)

                ordering = iter(priortized)
                order = next(ordering)
                group, asscending = deque([order[0]]), order[1]
                while True:
                    order = next(ordering, None)

                    if order and asscending == order[1]: group.append(order[0])
                    else:
                        if group:
                            path = self.nameOrderAsc if asscending else self.nameOrderDesc
                            path = normalizer.normalize(path)
                            target.append((path, self.separatorValue.join(group)))

                        if not order: break
                        group.clear()
                        group.append(order[0])
                        asscending = order[1]

        return exploit

    def encodeInvoker(self, invoker):
        '''
        Create an encode exploit for the invoker.
        
        @param invoker: Invoker
            The invoker to create a parameters encoder for.
        @return: callable(**data)
            The exploit that provides the invoker encoding.
        '''
        assert isinstance(invoker, Invoker), 'Invalid invoker %s' % invoker

        children, ordered = OrderedDict(), OrderedDict()
        for inp in invoker.inputs:
            assert isinstance(inp, Input)
            typeInp = inp.type
            assert isinstance(typeInp, Type)

            if typeInp.isPrimitive:
                children[inp.name] = self.encodePrimitive(typeInp, getterOnDict(inp.name))

            elif isinstance(typeInp, TypeQuery):
                assert isinstance(typeInp, TypeQuery)

                childrenQuery, orderedQuery, getterQuery = OrderedDict(), OrderedDict(), getterOnDict(inp.name)
                for nameEntry, classCriteria in typeInp.query.criterias.items():

                    getter = getterChain(getterQuery, getterOnObjIfIn(nameEntry, typeInp.childTypeFor(nameEntry)))
                    childrenQuery[nameEntry] = self.encodeCriteria(typeFor(classCriteria), getter)

                    if issubclass(classCriteria, AsOrdered):
                        orderedQuery[nameEntry] = self.encodeGetOrder(typeInp.childTypeFor(nameEntry), getterQuery)

                isUpdated = False
                if invoker.output.isOf(typeInp.owner):
                    # If the query is a main query and also there is no name conflict then add the query children to
                    # the main children
                    if set(childrenQuery.keys()).isdisjoint(children.keys()) and set(orderedQuery).isdisjoint(ordered):
                        isUpdated = True
                        children.update(childrenQuery)
                        ordered.update(orderedQuery)

                if not isUpdated:
                    children[inp.name] = self.encodePath(childrenQuery)
                    ordered[inp.name] = self.encodePath(orderedQuery)

        exploitOrder = None
        if ordered:
            if self.nameOrderAsc in children: log.error('Name conflict for \'%s\' in %s', self.nameOrderAsc, invoker)
            elif self.nameOrderDesc in children: log.error('Name conflict for \'%s\' in %s', self.nameOrderDesc, invoker)
            else: exploitOrder = self.encodeOrder(self.encodePath(ordered))
        exploitPath = self.encodePath(children)
        def exploit(**data):
            target = deque()
            data.update(target=target)
            exploitPath(**data)
            if exploitOrder: exploitOrder(**data)
            return target

        return exploit
