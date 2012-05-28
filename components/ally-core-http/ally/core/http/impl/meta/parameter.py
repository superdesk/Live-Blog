'''
Created on May 21, 2012

@package: ally core
@copyright: 2012 Sourcefabric o.p.s.
@license: http://www.gnu.org/licenses/gpl-3.0.txt
@author: Gabriel Nistor

Provides the parameters meta encoders and decoders.
'''

from ally.api.criteria import AsOrdered
from ally.api.operator.container import Criteria
from ally.api.operator.type import TypeQuery, TypeCriteriaEntry, TypeCriteria
from ally.api.type import Type, Input, Iter
from ally.container.ioc import injected
from ally.core.impl.meta.decode import DecodeObject, DecodeList, DecodeValue, \
    DecodeFirst, DecodeSetValue, DecodeGetter, DecodeSplit
from ally.core.impl.meta.encode import EncodeValue, EncodeCollection, \
    EncodeObject, EncodeGetter, EncodeMerge, EncodeObjectExploded, EncodeGetValue, \
    EncodeGetterIdentifier, EncodeIdentifier, EncodeJoin
from ally.core.impl.meta.general import getterOnDict, setterOnDict, getterOnObj, \
    getterChain, setterWithGetter, setterOnObj, setterToOthers, obtainOnDict, \
    getterOnObjIfIn, obtainOnObj, ContextParse
from ally.core.spec.meta import IMetaService, Value, Object, SAMPLE, Collection
from ally.core.spec.resources import Invoker, Normalizer
from collections import deque, Iterable
import logging
import random
import re

# --------------------------------------------------------------------

log = logging.getLogger(__name__)

# --------------------------------------------------------------------

@injected
class ParameterMetaService(IMetaService):
    '''
    @see: IMetaService impementation for handling the parameters meta.
    This service will provide a decode meta that will be able to take as identifiers:
        string, list[string], tuple(string), deque[string]
    '''

    separatorName = '.'
    # The separator used for parameter names.
    separatorOrderName = '.'
    # The separator used for the names in the ordering
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
        assert isinstance(self.separatorOrderName, str), 'Invalid separator for order names %s' % self.separatorOrderName
        assert isinstance(self.nameOrderAsc, str), 'Invalid name for ascending %s' % self.nameOrderAsc
        assert isinstance(self.nameOrderDesc, str), 'Invalid name for descending %s' % self.nameOrderDesc
        assert isinstance(self.regexSplitValues, str), 'Invalid regex for values split %s' % self.regexSplitValues
        assert isinstance(self.separatorValue, str), 'Invalid separator for values %s' % self.separatorValue
        assert isinstance(self.regexNormalizeValue, str), \
        'Invalid regex for value normalize %s' % self.regexNormalizeValue
        assert isinstance(self.separatorValueEscape, str), \
        'Invalid separator escape for values %s' % self.separatorValueEscape

        self.reSplitValues = re.compile(self.regexSplitValues)
        self.reNormalizeValue = re.compile(self.regexNormalizeValue)

    def createDecode(self, invoker):
        '''
        @see: IMetaService.createDecode
        '''
        assert isinstance(invoker, Invoker), 'Invalid invoker %s' % invoker

        root, ordering = DecodeParameters(self.separatorName), {}

        queries = deque()
        # We first process the primitive types.
        for inp in invoker.inputs:
            assert isinstance(inp, Input)
            typ = inp.type
            assert isinstance(typ, Type)

            if typ.isPrimitive:
                if typ.isOf(Iter):
                    assert isinstance(typ, Iter)
                    dprimitive = DecodeList(DecodeValue(list.append, typ.itemType))
                    dprimitive = DecodeSplit(dprimitive, self.reSplitValues, self.reNormalizeValue)
                    dprimitive = DecodeGetter(obtainOnDict(inp.name, list), dprimitive)
                else:
                    dprimitive = DecodeValue(setterOnDict(inp.name), typ)

                root.properties[inp.name] = dprimitive
            elif isinstance(typ, TypeQuery):
                assert isinstance(typ, TypeQuery)
                queries.append(inp)

        if queries:
            # We find out the model provided by the invoker
            mainq = [(inp, k) for k, inp in enumerate(queries) if invoker.output.isOf(inp.type.owner)]
            if len(mainq) == 1:
                # If we just have one main query that has the return type model as the owner we can strip the input
                # name from the criteria names.
                inp, k = mainq[0]
                del queries[k]
                self.decodeQuery(inp.type, obtainOnDict(inp.name, inp.type.forClass), root.properties, ordering)

            for inp in queries:
                dquery = root.properties[inp.name] = DecodeObject()
                qordering = ordering[inp.name] = DecodeObject()
                getter = obtainOnDict(inp.name, inp.type.forClass)

                self.decodeQuery(inp.type, getter, dquery.properties, qordering.properties)

        for name, asscending in ((self.nameOrderAsc, True), (self.nameOrderDesc, False)):
            if name in root.properties:
                log.error('Name conflict for %r in %s', name, invoker)
            else:
                order = DecodeOrdering(self.separatorOrderName, asscending)
                order.properties.update(ordering)
                root.properties[name] = DecodeSplit(order, self.reSplitValues, self.reNormalizeValue)

        return root

    def decodeQuery(self, queryType, getterQuery, decoders, ordering):
        '''
        Processes the query type and provides decoders and ordering decoders for it.
        
        @param queryType: TypeQuery
            The query type to process.
        @param getterQuery: callable(object)
            The call that provides the query instance object.
        @param decoders: dictionary{string, MetaDecode)
            The dictionary where the decoders for the query will be placed.
        @param ordering: dictionary{string, MetaDecode)
            The dictionary where the ordering decoders for the query will be placed.
        '''
        assert isinstance(queryType, TypeQuery), 'Invalid query type %s' % queryType
        assert callable(getterQuery), 'Invalid query object getter %s' % getterQuery
        assert isinstance(decoders, dict), 'Invalid decoders %s' % decoders
        assert isinstance(ordering, dict), 'Invalid ordering %s' % ordering

        for etype in queryType.childTypes():
            assert isinstance(etype, TypeCriteriaEntry)
            ctype, criteria = etype.criteriaType, etype.criteria
            assert isinstance(ctype, TypeCriteria)
            assert isinstance(criteria, Criteria)

            if etype.name in decoders:
                log.error('Name conflict for criteria %r decoder from %s', etype.name, queryType)
            else:
                getterCriteria = getterChain(getterQuery, getterOnObj(etype.name))
                if criteria.main:
                    dmain = decoders[etype.name] = DecodeFirst()

                    setterMain = setterToOthers(*[setterOnObj(main) for main in criteria.main])
                    setterMain = setterWithGetter(getterCriteria, setterMain)

                    dmain.decoders.append(DecodeValue(setterMain, criteria.properties[criteria.main[0]]))

                    dcriteria = DecodeObject()
                    dmain.decoders.append(dcriteria)
                else:
                    dcriteria = decoders[etype.name] = DecodeObject()

                if issubclass(etype.forClass, AsOrdered): exclude = ('ascending', 'priority')
                else: exclude = ()

                for prop, typ in criteria.properties.items():
                    if prop in exclude: continue
                    if typ.isOf(Iter):
                        assert isinstance(typ, Iter)
                        dprop = DecodeList(DecodeValue(list.append, typ.itemType))
                        dprop = DecodeSplit(dprop, self.reSplitValues, self.reNormalizeValue)
                        dprop = DecodeGetter(getterChain(getterCriteria, obtainOnObj(prop, list)), dprop)
                    else:
                        dprop = DecodeValue(setterWithGetter(getterCriteria, setterOnObj(prop)), typ)

                    dcriteria.properties[prop] = dprop

            if issubclass(etype.forClass, AsOrdered):
                if etype.name in ordering:
                    log.error('Name conflict for criteria %r ordering from %s', etype.name, queryType)
                else:
                    ordering[etype.name] = DecodeGetter(getterQuery, DecodeSetValue(setterOrdering(etype)))

    # ----------------------------------------------------------------

    def createEncode(self, invoker):
        '''
        @see: IMetaService.createEncode
        '''
        assert isinstance(invoker, Invoker), 'Invalid invoker %s' % invoker

        root = EncodeParameters(self.separatorName)

        queries = deque()
        # We first process the primitive types.
        for inp in invoker.inputs:
            assert isinstance(inp, Input)
            typ = inp.type
            assert isinstance(typ, Type)

            if typ.isPrimitive:
                if typ.isOf(Iter):
                    assert isinstance(typ, Iter)
                    eprimitive = EncodeCollection(EncodeValue(typ.itemType))
                    eprimitive = EncodeJoin(eprimitive, self.separatorValue, self.separatorValueEscape)
                else: eprimitive = EncodeValue(typ)

                eprimitive = EncodeGetterIdentifier(eprimitive, getterOnDict(inp.name), inp.name)
                root.properties.append(eprimitive)
            elif isinstance(typ, TypeQuery):
                assert isinstance(typ, TypeQuery)
                queries.append(inp)

        ordering = EncodeOrdering(self.nameOrderAsc, self.nameOrderDesc, self.separatorOrderName)

        if queries:
            # We find out the model provided by the invoker
            mainq, main = [inp for inp in queries if invoker.output.isOf(inp.type.owner)], None
            if len(mainq) == 1:
                # If we just have one main query that has the return type model as the owner we can strip the input
                # name from the criteria names.
                main = mainq[0]

            for inp in queries:
                getter = getterOnDict(inp.name)

                equery = EncodeObject()
                qordering = EncodeObject()

                if inp == main:
                    root.properties.append(EncodeGetter(equery, getter))
                    ordering.properties.append(EncodeGetter(qordering, getter))
                else:
                    root.properties.append(EncodeGetterIdentifier(equery, getter, inp.name))
                    ordering.properties.append(EncodeGetterIdentifier(qordering, getter, inp.name))

                self.encodeQuery(inp.type, equery.properties, qordering.properties)

        root.properties.append(EncodeJoin(ordering, self.separatorValue, self.separatorValueEscape))

        return root

    def encodeQuery(self, queryType, encoders, ordering):
        '''
        Processes the query type and provides encoders and ordering encoders for it.
        
        @param queryType: TypeQuery
            The query type to process.
        @param decoders: dictionary{string, MetaDecode)
            The dictionary where the decoders for the query will be placed.
        @param ordering: dictionary{string, MetaDecode)
            The dictionary where the ordering decoders for the query will be placed.
        '''
        assert isinstance(queryType, TypeQuery), 'Invalid query type %s' % queryType
        assert isinstance(encoders, list), 'Invalid encoders %s' % encoders
        assert isinstance(ordering, list), 'Invalid ordering %s' % ordering

        for etype in queryType.childTypes():
            assert isinstance(etype, TypeCriteriaEntry)
            ctype, criteria = etype.criteriaType, etype.criteria
            assert isinstance(ctype, TypeCriteria)
            assert isinstance(criteria, Criteria)

            exclude = set()
            if criteria.main:
                exclude.update(criteria.main)

                merge = EncodeMerge(etype.name)
                for prop in criteria.main:
                    pencode = self.encodePrimitive(prop, criteria.properties[prop])
                    merge.assign(EncodeGet(getterOnObjIfIn(prop, ctype.childTypeFor(prop)), pencode))
            else:
                cencode = EncodeObject(etype.name)
                encoders.append(EncodeGet(getterOnObjIfIn(etype.name, etype), cencode))
                encoders = cencode.properties

            if issubclass(etype.forClass, AsOrdered): exclude.update(('ascending', 'priority'))

            for prop, typ in criteria.properties.items():
                if prop in exclude: continue
                if typ.isOf(Iter):
                    assert isinstance(typ, Iter)
                    eprop = EncodeCollection(EncodeValue(typ.itemType))
                    eprop = EncodeJoin(eprop, self.separatorValue, self.separatorValueEscape)
                else: eprop = EncodeValue(typ)

                eprop = EncodeGetterIdentifier(eprop, getterOnObjIfIn(prop, ctype.childTypeFor(prop)), prop)
                if prop in criteria.main: emain.encoders.append(eprop)
                else: ecrtieria.properties.append(eprop)

            if issubclass(etype.forClass, AsOrdered):
                eorder = EncodeGetValue(getterOrdering(etype))
                eorder = EncodeIdentifier(eorder, etype.name)
                ordering.append(eorder)

# --------------------------------------------------------------------

def setterOrdering(entryType):
    '''
    Create a setter specific for the AsOrdered criteria.
    
    @param entryType: TypeCriteriaEntry
        The criteria entry type of the AsOrdered criteria to manage.
    '''
    assert isinstance(entryType, TypeCriteriaEntry), 'Invalid entry type %s' % entryType
    assert isinstance(entryType.parent, TypeQuery)

    def setter(obj, value):
        assert entryType.parent.isValid(obj), 'Invalid query object %s' % obj
        # We first find the biggest priority in the query
        priority = 0
        for etype in entryType.parent.childTypes():
            assert isinstance(etype, TypeCriteriaEntry)
            if etype == entryType: continue
            if not issubclass(etype.forClass, AsOrdered): continue

            if etype in obj:
                criteria = getattr(obj, etype.name)
                assert isinstance(criteria, AsOrdered), 'Invalid criteria %s' % criteria
                if AsOrdered.priority in criteria: priority = max(priority, criteria.priority)

        criteria = getattr(obj, entryType.name)
        assert isinstance(criteria, AsOrdered), 'Invalid criteria %s' % criteria
        criteria.ascending = value
        criteria.priority = priority + 1
    return setter

class DecodeOrdering(DecodeObject):
    '''
    Provides the decoding for the ordering parameters.
    '''

    def __init__(self, separator, ascending):
        '''
        Construct the decoding order.
        
        @param separator: string
            The separator used for the criteria to be ordered.
        @param ascending: boolean
            The value used to be set on the setters.
            
        @ivar decoders: dictionary{string, MetaDecode}
            A dictionary that will be used for the ordering decoding.
        '''
        assert isinstance(separator, str), 'Invalid separator %s' % separator
        assert isinstance(ascending, bool), 'Invalid ascending flag %s' % ascending
        super().__init__()

        self.separator = separator
        self.ascending = ascending

    def decode(self, paths, value, obj, context):
        '''
        MetaDecode.decode
        '''
        assert isinstance(paths, deque), 'Invalid paths %s' % paths

        if paths: return False

        if isinstance(value, (list, tuple)): values = value
        else: values = [value]

        for value in values:
            if not isinstance(value, str): return False
            else:
                if not super().decode(deque(value.split(self.separator)), self.ascending, obj, context): return False

        return True

class DecodeParameters(DecodeObject):
    '''
    Provides the parameters decode. It will split the string identifiers based on the separator.
    '''

    def __init__(self, separator):
        '''
        Construct the decoder.
        
        @param separator: string
            The separator to be used for converting the string identifier.
        @param root: IMetaDecode
            The root meta decode, usually this meta decode and its children only accept deque[string].
        '''
        assert isinstance(separator, str), 'Invalid separator %s' % separator
        super().__init__()

        self.separator = separator

    def decode(self, identifier, value, obj, context):
        '''
        @see: IMetaDecode.decode
        '''
        if isinstance(identifier, str): identifier = identifier.split(self.separator)
        if isinstance(identifier, (list, tuple)): identifier = deque(identifier)

        if not isinstance(identifier, deque): return False

        return super().decode(identifier, value, obj, context)

# --------------------------------------------------------------------

def getterOrdering(entryType):
    '''
    Create a getter specific for the AsOrdered criteria.
    
    @param entryType: TypeCriteriaEntry
        The criteria entry type of the AsOrdered criteria to manage.
    '''
    assert isinstance(entryType, TypeCriteriaEntry), 'Invalid entry type %s' % entryType
    assert isinstance(entryType.parent, TypeQuery)

    def getter(obj):
        assert entryType.parent.isValid(obj), 'Invalid query object %s' % obj

        if entryType in obj:
            criteria = getattr(obj, entryType.name)
            assert isinstance(criteria, AsOrdered), 'Invalid criteria %s' % criteria
            if AsOrdered.ascending in criteria: return (criteria.ascending, criteria.priority)
    return getter

class EncodeOrdering(EncodeObjectExploded):
    '''
    Provides the encoding for the ordering parameters.
    '''

    def __init__(self, nameOrderAsc, nameOrderDesc, separator):
        '''
        Construct the order encoder.
        
        @param nameOrderAsc: string
            The identifier used for ascending order.
        @param nameOrderDesc: string
            The identifier used for descending order.
        @param separator: string
            The separator used for the criteria to be ordered.
        @param separator: string
            The separator used for the criteria to be ordered.
        '''
        assert isinstance(nameOrderAsc, str), 'Invalid order ascending name %s' % nameOrderAsc
        assert isinstance(nameOrderDesc, str), 'Invalid order descending name %s' % nameOrderDesc
        assert isinstance(separator, str), 'Invalid separator %s' % separator
        super().__init__()

        self.nameOrderAsc = nameOrderAsc
        self.nameOrderDesc = nameOrderDesc
        self.separator = separator

    def encode(self, obj, context):
        '''
        IMetaEncode.encode
        '''
        assert isinstance(context, ContextParse), 'Invalid context %s' % context
        assert isinstance(context.normalizer, Normalizer)
        normalize = context.normalizer.normalize

        metaObject = super().encode(obj, context)
        if metaObject is None: return
        assert isinstance(metaObject, Object)

        ordering, priortized = [], []
        for meta in metaObject.properties:
            assert isinstance(meta, Value), 'Invalid meta %s' % meta
            if meta.value is SAMPLE:
                asscending, priority = random.choice((True, False)), random.randint(0, 10)
            else:
                assert isinstance(meta.value, tuple), 'The meta value needs to be a two items tuple %s' % meta.value
                asscending, priority = meta.value
            if asscending is not None:
                if isinstance(meta.identifier, str): identifier = normalize(meta.identifier)
                else:
                    assert isinstance(meta.identifier, (tuple, list)), 'Invalid identifier %s' % meta.identifier
                    identifier = self.separator.join(normalize(iden) for iden in meta.identifier)

                if priority is None: ordering.append((identifier, asscending))
                else: priortized.append((identifier, asscending, priority))

        if not priortized and not ordering: return

        priortized.sort(key=lambda order: not order[1]) # Order by asc/desc
        priortized.sort(key=lambda order: order[2]) # Order by priority

        ordering.sort(key=lambda order: not order[1]) # Order by asc/desc
        priortized.extend(ordering)

        return Object(properties=self.groupMeta(priortized, normalize(self.nameOrderAsc), normalize(self.nameOrderDesc)))

    def groupMeta(self, ordering, nameAsc, nameDesc):
        '''
        Yields the meta's grouped based on the ascending and descending if they are in consecutive order.
        
        @param ordering: list[tuple(string, boolean)]
            A list containing tuples that have on the first position the ordered identifier and on the second position
            True for ascending and False for descending.
        '''
        assert isinstance(ordering, list), 'Invalid ordering %s' % ordering
        assert ordering, 'Invalid ordering %s with no elements' % ordering

        ordering = iter(ordering)
        ord = next(ordering)
        group, asscending = deque([ord[0]]), ord[1]
        while True:
            ord = next(ordering, None)

            if ord and asscending == ord[1]: group.append(ord[0])
            else:
                if group:
                    if len(group) > 1:
                        yield Collection(nameAsc if asscending else nameDesc, (Value(value=value) for value in group))
                    else:
                        yield Value(nameAsc if asscending else nameDesc, group[0])

                if not ord: break
                group.clear()
                group.append(ord[0])
                asscending = ord[1]

class EncodeParameters(EncodeObjectExploded):
    '''
    Provides the parameters encode. It will explode the contained meta's and join the identifiers based on the
    separator.  
    '''

    def __init__(self, separator):
        '''
        Construct the encoder.
        
        @param separator: string
            The separator to be used for joining the string identifier.
        '''
        assert isinstance(separator, str), 'Invalid separator %s' % separator
        super().__init__()

        self.separator = separator

    def encode(self, obj, context):
        '''
        IMetaEncode.encode
        '''
        meta = super().encode(obj, context)
        if meta is not None:
            assert isinstance(meta, Object), 'Invalid meta object %s' % meta
            meta.properties = self.joinIdentifiers(meta.properties)
            return meta

    def joinIdentifiers(self, metas):
        '''
        Join the identifiers from the provided metas.
        
        @param metas: Iterable[Meta]
            The meta's to join the identifiers for.
        '''
        assert isinstance(metas, Iterable), 'Invalid meta\'s' % metas
        for meta in metas:
            assert isinstance(meta, Value), 'Invalid meta %s, only Value expected' % meta
            if isinstance(meta.identifier, (list, tuple)):
                meta.identifier = self.separator.join(meta.identifier)
            yield meta

