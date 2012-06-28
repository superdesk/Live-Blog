'''
Created on May 25, 2012

@package: ally core http
@copyright: 2011 Sourcefabric o.p.s.
@license: http://www.gnu.org/licenses/gpl-3.0.txt
@author: Gabriel Nistor

Provides the parameters handler.
'''

from ally.api.criteria import AsOrdered
from ally.api.operator.container import Criteria
from ally.api.operator.type import TypeQuery, TypeCriteriaEntry, TypeCriteria
from ally.api.type import Input, Type, Iter
from ally.container.ioc import injected
from ally.core.impl.transforming.decode import valueListExplode, \
    targetSetConvertedValue, valueSplit, targetGetter, targetSetValue, locatorSplit, \
    locatorNormalized
from ally.core.impl.transforming.support import obtainOnDict, setterOnDict, \
    getterChain, getterOnObj, setterToOthers, setterOnObj, setterWithGetter, \
    obtainOnObj, getterOnDict
from ally.core.spec.resources import Invoker, Normalizer
from ally.design.exploit import Exploit, PRIVATE, IResolve, locatorIn, NORMAL, \
    locatorNormal
from collections import deque
import logging
import random
import re
from ally.core.impl.transforming.render import renderCollection, renderConverted, \
    valueGetter, placeName, placeNameAndGetter, renderJoin

# --------------------------------------------------------------------

log = logging.getLogger(__name__)

# --------------------------------------------------------------------

@injected
class ParameterTransformer:
    '''
    Implementation that provides the parameters transformation.
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

        self._reSplitValues = re.compile(self.regexSplitValues)
        self._reNormalizeValue = re.compile(self.regexNormalizeValue)

    # ----------------------------------------------------------------

    def createDecode(self, invoker):
        '''
        Create the parameter decoder for the provided invoker.
        
        @param invoker: Invoker
            The invoker to create a parameters decoder for.
        @return: Exploit
            The exploit that provides the parameters decoding.
        '''
        assert isinstance(invoker, Invoker), 'Invalid invoker %s' % invoker

        main = Exploit(locator=locatorSplit(locatorNormalized(), self.separatorName))
        order = Exploit(status=PRIVATE)

        queries = deque()
        # We first process the primitive types.
        for inp in invoker.inputs:
            assert isinstance(inp, Input)
            typ = inp.type
            assert isinstance(typ, Type)

            if typ.isPrimitive:
                if isinstance(typ, Iter):
                    assert isinstance(typ, Iter)

                    setter = setterWithGetter(obtainOnDict(inp.name, list), list.append)
                    eprimitive = valueListExplode(targetSetConvertedValue(setter, typ.itemType))
                    eprimitive = valueSplit(eprimitive, self._reSplitValues, self._reNormalizeValue)
                else:
                    eprimitive = targetSetConvertedValue(setterOnDict(inp.name), typ)
                main[inp.name] = Exploit(eprimitive)

            elif isinstance(typ, TypeQuery):
                assert isinstance(typ, TypeQuery)

                queries.append(inp)

        if queries:
            # We find out the model provided by the invoker
            mainq = [k for k, inp in enumerate(queries) if invoker.output.isOf(inp.type.owner)]
            if len(mainq) == 1:
                # If we just have one main query that has the return type model as the owner we can strip the input
                # name from the criteria names.
                inp = queries[mainq[0]]
                del queries[mainq[0]]
                self.decodeQuery(inp.type, obtainOnDict(inp.name, inp.type.clazz), main, order)

            for inp in queries:
                self.decodeQuery(inp.type, obtainOnDict(inp.name, inp.type.clazz),
                                 main.add(inp.name, Exploit()), order.add(inp.name, Exploit()))

        locator = locatorIn(locatorNormalized(), 'order')
        for name, ascending in ((self.nameOrderAsc, True), (self.nameOrderDesc, False)):
            if name in main:
                log.error('Name conflict for %r in %s', name, invoker)
            else:
                eorder = processOrder(self.separatorOrderName, ascending)
                eorder = valueSplit(eorder, self._reSplitValues, self._reNormalizeValue)
                main[name] = ordering = Exploit(eorder, locator)
                ordering['order'] = order

        return main

    def decodeQuery(self, queryType, getterQuery, main, order):
        '''
        Processes the query type and provides decoders and ordering decoders for it.
        
        @param queryType: TypeQuery
            The query type to process.
        @param getterQuery: callable(object)
            The call that provides the query instance object.
        @param main: Exploit
            The exploit where the decoders for the query will be placed.
        @param order: Exploit
            The exploit where the ordering decoders for the query will be placed.
        '''
        assert isinstance(queryType, TypeQuery), 'Invalid query type %s' % queryType
        assert callable(getterQuery), 'Invalid query object getter %s' % getterQuery
        assert isinstance(main, Exploit), 'Invalid main exploit %s' % main
        assert isinstance(order, Exploit), 'Invalid ordering exploit %s' % order

        for etype in queryType.childTypes():
            assert isinstance(etype, TypeCriteriaEntry)
            ctype, criteria = etype.criteriaType, etype.criteria
            assert isinstance(ctype, TypeCriteria)
            assert isinstance(criteria, Criteria)

            if etype.name in main:
                log.error('Name conflict for criteria \'%s\' decoder from %s', etype.name, queryType)
            else:
                getterCriteria = getterChain(getterQuery, getterOnObj(etype.name))
                if criteria.main:
                    setterMain = setterToOthers(*(setterOnObj(name) for name in criteria.main))
                    setterMain = setterWithGetter(getterCriteria, setterMain)
                    ecriteria = targetSetConvertedValue(setterMain, criteria.properties[criteria.main[0]])
                    main[etype.name] = crit = Exploit(ecriteria)

                if etype.isOf(AsOrdered): exclude = ('ascending', 'priority')
                else: exclude = ()

                for prop, propType in criteria.properties.items():
                    if prop in exclude: continue
                    if isinstance(propType, Iter):
                        assert isinstance(propType, Iter)
                        setter = setterWithGetter(getterChain(getterCriteria, obtainOnObj(prop, list)), list.append)
                        eprop = valueListExplode(targetSetConvertedValue(setter, propType.itemType))
                        eprop = valueSplit(eprop, self._reSplitValues, self._reNormalizeValue)
                    else:
                        eprop = targetSetConvertedValue(setterWithGetter(getterCriteria, setterOnObj(prop)), propType)
                    crit[prop] = Exploit(eprop)

            if etype.isOf(AsOrdered):
                if etype.name in order:
                    log.error('Name conflict for criteria \'%s\' ordering from %s', etype.name, queryType)
                else:
                    eorder = targetGetter(targetSetValue(setterOrdering(etype)), getterQuery)
                    order[etype.name] = Exploit(eorder)

    # ----------------------------------------------------------------

    def createEncode(self, invoker):
        '''
        Create the encode for the provided invoker.
        '''
        assert isinstance(invoker, Invoker), 'Invalid invoker %s' % invoker

        main, order = Exploit(locatorNormal()), Exploit()

        queries = deque()
        # We first process the primitive types.
        for inp in invoker.inputs:
            assert isinstance(inp, Input)
            typ = inp.type
            assert isinstance(typ, Type)

            getter = getterOnDict(inp.name)
            if typ.isPrimitive:
                if isinstance(typ, Iter):
                    assert isinstance(typ, Iter)

                    eprimitive = renderCollection(typ.itemType)
                    eprimitive = placeNameAndGetter(eprimitive, getter, inp.name)
                    eprimitive = renderJoin(eprimitive, self.separatorValue, self.separatorValueEscape)
                    main[inp.name] = primitive = Exploit(eprimitive)
                    primitive.add(typ.itemType, Exploit(renderConverted(typ.itemType)))

                else:
                    eprimitive = renderConverted(typ)
                    eprimitive = placeNameAndGetter(eprimitive, getter, inp.name)
                    main[inp.name] = Exploit(valueGetter(eprimitive, getter))

            elif isinstance(typ, TypeQuery):
                assert isinstance(typ, TypeQuery)

                queries.append(inp)

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

        ordering = EncodeOrdering(ordering, self.nameOrderAsc, self.nameOrderDesc, self.separatorOrderName)
        ordering = EncodeJoin(ordering, self.separatorValue, self.separatorValueEscape)
        root.properties.append(ordering)

        return EncodeJoinIndentifier(root, self.separatorName)

    def encodeQuery(self, queryType, main, order):
        '''
        Processes the query type and provides encoders and ordering encoders for it.
        
        @param queryType: TypeQuery
            The query type to process.
        @param main: Exploit
            The exploit where the encoders for the query will be placed.
        @param order: Exploit
            The exploit where the ordering encoders for the query will be placed.
        '''
        assert isinstance(queryType, TypeQuery), 'Invalid query type %s' % queryType
        assert isinstance(main, Exploit), 'Invalid main exploit %s' % main
        assert isinstance(order, Exploit), 'Invalid ordering exploit %s' % order

        for etype in queryType.childTypes():
            assert isinstance(etype, TypeCriteriaEntry)
            ctype, criteria = etype.criteriaType, etype.criteria
            assert isinstance(ctype, TypeCriteria)
            assert isinstance(criteria, Criteria)

            ecrtieria = EncodeObject()
            encoders.append(EncodeGetterIdentifier(ecrtieria, getterOnObjIfIn(etype.name, etype), etype.name))

            if criteria.main:
                emain = EncodeMerge()
                ecrtieria.properties.append(emain)

            if etype.isOf(AsOrdered): exclude = ('ascending', 'priority')
            else: exclude = ()

            for prop, typ in criteria.properties.items():
                if prop in exclude: continue
                if isinstance(typ, Iter):
                    assert isinstance(typ, Iter)
                    eprop = EncodeCollection(EncodeValue(typ.itemType))
                    eprop = EncodeJoin(eprop, self.separatorValue, self.separatorValueEscape)
                else: eprop = EncodeValue(typ)

                eprop = EncodeGetterIdentifier(eprop, getterOnObjIfIn(prop, ctype.childTypeFor(prop)), prop)
                if prop in criteria.main: emain.encoders.append(eprop)
                else: ecrtieria.properties.append(eprop)

            if etype.isOf(AsOrdered):
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
            if not etype.isOf(AsOrdered): continue

            if etype in obj:
                criteria = getattr(obj, etype.name)
                assert isinstance(criteria, AsOrdered), 'Invalid criteria %s' % criteria
                if AsOrdered.priority in criteria: priority = max(priority, criteria.priority)

        criteria = getattr(obj, entryType.name)
        assert isinstance(criteria, AsOrdered), 'Invalid criteria %s' % criteria
        criteria.ascending = value
        criteria.priority = priority + 1
    return setter

def processOrder(separator, ascending):
    '''
    Provides the ordering exploit dispatch.
    
    @param separator: string
        The separator used for the criteria to be ordered.
    @param ascending: boolean
        The value used to be set on the setters.
    '''
    assert isinstance(separator, str), 'Invalid separator %s' % separator
    assert isinstance(ascending, bool), 'Invalid ascending flag %s' % ascending

    def exploit(value, resolve, **data):
        assert isinstance(resolve, IResolve), 'Invalid resolve %s' % resolve

        if isinstance(value, (list, tuple)): values = value
        else: values = (value,)

        for value in values:
            if not isinstance(value, str): return False
            else:
                if not resolve.request(*value.split(separator), value=ascending, **data): return False
        return resolve.doAll()
    return exploit

# --------------------------------------------------------------------
#
#def getterOrdering(entryType):
#    '''
#    Create a getter specific for the AsOrdered criteria.
#    
#    @param entryType: TypeCriteriaEntry
#        The criteria entry type of the AsOrdered criteria to manage.
#    '''
#    assert isinstance(entryType, TypeCriteriaEntry), 'Invalid entry type %s' % entryType
#    assert isinstance(entryType.parent, TypeQuery)
#
#    def getter(obj):
#        assert entryType.parent.isValid(obj), 'Invalid query object %s' % obj
#
#        if entryType in obj:
#            criteria = getattr(obj, entryType.name)
#            assert isinstance(criteria, AsOrdered), 'Invalid criteria %s' % criteria
#            if AsOrdered.ascending in criteria: return (criteria.ascending, criteria.priority)
#    return getter
#
#class EncodeOrdering(EncodeExploded):
#    '''
#    Provides the encoding for the ordering parameters.
#    '''
#
#    def __init__(self, encoder, nameOrderAsc, nameOrderDesc, separator):
#        '''
#        Construct the order encoder.
#        
#        @param nameOrderAsc: string
#            The identifier used for ascending order.
#        @param nameOrderDesc: string
#            The identifier used for descending order.
#        @param separator: string
#            The separator used for the criteria to be ordered.
#        '''
#        assert isinstance(nameOrderAsc, str), 'Invalid order ascending name %s' % nameOrderAsc
#        assert isinstance(nameOrderDesc, str), 'Invalid order descending name %s' % nameOrderDesc
#        assert isinstance(separator, str), 'Invalid separator %s' % separator
#        super().__init__(encoder)
#
#        self.nameOrderAsc = nameOrderAsc
#        self.nameOrderDesc = nameOrderDesc
#        self.separator = separator
#
#    def encode(self, obj, context):
#        '''
#        IMetaEncode.encode
#        '''
#        assert isinstance(context, Conversion), 'Invalid context %s' % context
#        assert isinstance(context.normalizer, Normalizer), 'Invalid normalizer %s' % context.normalizer
#        normalize = context.normalizer.normalize
#
#        metaCollection = super().encode(obj, context)
#        if metaCollection is None: return
#        assert isinstance(metaCollection, Collection)
#
#        ordering, priortized = [], []
#        for meta in metaCollection.items:
#            assert isinstance(meta, Value), 'Invalid meta %s' % meta
#            if meta.value is SAMPLE:
#                asscending, priority = random.choice((True, False)), random.randint(0, 10)
#            else:
#                assert isinstance(meta.value, tuple), 'The meta value needs to be a two items tuple %s' % meta.value
#                asscending, priority = meta.value
#            if asscending is not None:
#                if isinstance(meta.identifier, str): identifier = normalize(meta.identifier)
#                else:
#                    assert isinstance(meta.identifier, (tuple, list)), 'Invalid identifier %s' % meta.identifier
#                    identifier = self.separator.join(normalize(iden) for iden in meta.identifier)
#
#                if priority is None: ordering.append((identifier, asscending))
#                else: priortized.append((identifier, asscending, priority))
#
#        if not priortized and not ordering: return
#
#        priortized.sort(key=lambda order: not order[1]) # Order by asc/desc
#        priortized.sort(key=lambda order: order[2]) # Order by priority
#
#        ordering.sort(key=lambda order: not order[1]) # Order by asc/desc
#        priortized.extend(ordering)
#
#        return Collection(items=self.groupMeta(priortized, normalize(self.nameOrderAsc), normalize(self.nameOrderDesc)))
#
#    def groupMeta(self, ordering, nameAsc, nameDesc):
#        '''
#        Yields the meta's grouped based on the ascending and descending if they are in consecutive order.
#        
#        @param ordering: list[tuple(string, boolean)]
#            A list containing tuples that have on the first position the ordered identifier and on the second position
#            True for ascending and False for descending.
#        '''
#        assert isinstance(ordering, list), 'Invalid ordering %s' % ordering
#        assert ordering, 'Invalid ordering %s with no elements' % ordering
#
#        ordering = iter(ordering)
#        ord = next(ordering)
#        group, asscending = deque([ord[0]]), ord[1]
#        while True:
#            ord = next(ordering, None)
#
#            if ord and asscending == ord[1]: group.append(ord[0])
#            else:
#                if group:
#                    if len(group) > 1:
#                        yield Collection(nameAsc if asscending else nameDesc, (Value(value=value) for value in group))
#                    else:
#                        yield Value(nameAsc if asscending else nameDesc, group[0])
#
#                if not ord: break
#                group.clear()
#                group.append(ord[0])
#                asscending = ord[1]
