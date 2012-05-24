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
from ally.api.operator.type import TypeQuery, TypeCriteriaEntry, TypeModel, \
    TypeModelProperty, TypeCriteria
from ally.api.type import Type, Input, List, Iter
from ally.container.ioc import injected
from ally.core.impl.meta.decode import DecodeNode, DecodeList, DecodeValue, \
    DecodeSequence, DecodeRootString, DecodeSet
from ally.core.impl.meta.encode import EncodeValue, EncodeCollection, \
    EncodeObject, EncodeGet, EncodeMerge
from ally.core.impl.meta.general import getterOnDict, setterOnDict, getterOnObj, \
    getterChain, setterWithGetter, setterOnObj, setterToOthers, obtainOnDict, \
    getSame, getterOnObjIfIn
from ally.core.spec.meta import IMetaService
from ally.core.spec.resources import Invoker
from ally.exception import DevelError
from collections import deque
import logging
from test.ally.test_support import EncoderGetObj

# --------------------------------------------------------------------

log = logging.getLogger(__name__)

# --------------------------------------------------------------------

@injected
class ParamMetaService(IMetaService):
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

    def __init__(self):
        assert isinstance(self.separatorName, str), 'Invalid separator for names %s' % self.separatorName
        assert isinstance(self.separatorOrderName, str), 'Invalid separator for order names %s' % self.separatorOrderName
        assert isinstance(self.nameOrderAsc, str), 'Invalid name for ascending %s' % self.nameOrderAsc
        assert isinstance(self.nameOrderDesc, str), 'Invalid name for descending %s' % self.nameOrderDesc

    def createDecode(self, invoker):
        '''
        @see: IMetaService.createDecode
        '''
        assert isinstance(invoker, Invoker), 'Invalid invoker %s' % invoker

        root, ordering = DecodeNode(), {}

        queries = deque()
        # We first process the primitive types.
        for inp in invoker.inputs:
            assert isinstance(inp, Input)
            typ = inp.type
            assert isinstance(typ, Type)

            if typ.isPrimitive:
                setter = setterOnDict(inp.name)
                if typ.isOf(Iter):
                    assert isinstance(typ, Iter)
                    pdecode = DecodeList(setter, getterOnDict(inp.name), DecodeValue(list.append, typ.itemType))
                else:
                    pdecode = DecodeValue(setter, typ)

                root.decoders[inp.name] = pdecode
            elif isinstance(typ, TypeQuery):
                assert isinstance(typ, TypeQuery)
                queries.append(inp)

        if queries:
            # We find out the model provided by the invoker
            mtype = self.findInvokerModel(invoker)
            if mtype:
                # First we need to find the main returned model query if available
                assert isinstance(mtype, TypeModel)
                mainq = [(inp, k) for k, inp in enumerate(queries) if inp.type.owner == mtype]
                if len(mainq) == 1:
                    # If we just have one main query that has the return type model as the owner we can strip the input
                    # name from the criteria names.
                    inp, k = mainq[0]
                    del queries[k]
                    self.decodeQuery(inp.type, obtainOnDict(inp.name, inp.type.forClass), root.decoders, ordering)

            for inp in queries:
                nodeDecoders = root.decoders[inp.name] = DecodeNode()
                nodeOrdering = ordering[inp.name] = DecodeNode()
                getter = obtainOnDict(inp.name, inp.type.forClass)

                self.decodeQuery(inp.type, getter, nodeDecoders.decoders, nodeOrdering.decoders)

        for name, asscending in ((self.nameOrderAsc, True), (self.nameOrderDesc, False)):
            if name in root.decoders:
                log.error('Name conflict for %r in %s', name, invoker)
            else:
                order = root.decoders[name] = DecodeOrdering(self.separatorOrderName, asscending)
                order.decoders.update(ordering)

        return DecodeRootString(self.separatorName, root)

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
                    sequence = decoders[etype.name] = DecodeSequence()

                    setterMain = setterToOthers(*[setterOnObj(main) for main in criteria.main])
                    setterMain = setterWithGetter(getterCriteria, setterMain)

                    sequence.decoders.append(DecodeValue(setterMain, criteria.properties[criteria.main[0]]))

                    node = DecodeNode()
                    sequence.decoders.append(node)
                else:
                    node = decoders[etype.name] = DecodeNode()

                for prop, propType in criteria.properties.items():
                    node.decoders[prop] = DecodeValue(setterWithGetter(getterCriteria, setterOnObj(prop)), propType)

            if issubclass(etype.forClass, AsOrdered):
                if etype.name in ordering:
                    log.error('Name conflict for criteria %r ordering from %s', etype.name, queryType)
                else:
                    ordering[etype.name] = DecodeSet(setterOrdering(getterQuery, etype))

    # ----------------------------------------------------------------

    def createEncode(self, invoker):
        '''
        @see: IMetaService.createEncode
        '''
        assert isinstance(invoker, Invoker), 'Invalid invoker %s' % invoker

        root, ordering = EncodeObject(), {}

        queries = deque()
        # We first process the primitive types.
        for inp in invoker.inputs:
            assert isinstance(inp, Input)
            typ = inp.type
            assert isinstance(typ, Type)

            if typ.isPrimitive:
                root.properties.append(EncodeGet(getterOnDict(inp.name), self.encodePrimitive(inp.name, typ)))
            elif isinstance(typ, TypeQuery):
                assert isinstance(typ, TypeQuery)
                queries.append(inp)

        if queries:
            # We find out the model provided by the invoker
            mtype = self.findInvokerModel(invoker)
            if mtype:
                # First we need to find the main returned model query if available
                assert isinstance(mtype, TypeModel)
                mainq = [(inp, k) for k, inp in enumerate(queries) if inp.type.owner == mtype]
                if len(mainq) == 1:
                    # If we just have one main query that has the return type model as the owner we can strip the input
                    # name from the criteria names.
                    inp, k = mainq[0]
                    del queries[k]
                    self.decodeQuery(inp.type, obtainOnDict(inp.name, inp.type.forClass), root.decoders, ordering)

            for inp in queries:
                nodeDecoders = root.decoders[inp.name] = DecodeNode()
                nodeOrdering = ordering[inp.name] = DecodeNode()
                getter = obtainOnDict(inp.name, inp.type.forClass)

                self.decodeQuery(inp.type, getter, nodeDecoders.decoders, nodeOrdering.decoders)

        for name, asscending in ((self.nameOrderAsc, True), (self.nameOrderDesc, False)):
            if name in root.decoders:
                log.error('Name conflict for %r in %s', name, invoker)
            else:
                order = root.decoders[name] = DecodeOrdering(self.separatorOrderName, asscending)
                order.decoders.update(ordering)

        return DecodeRootString(self.separatorName, root)

    def encodePrimitive(self, identifier, typ):
        '''
        Create an encode for a primitive type.
        
        @param identifier: object
            The identifier to use for the encode.
        @param typ: Type
            The primitive type to create the encode for.
        @return: MetaEncode
            The primitive meta encode.
        '''
        if typ.isOf(Iter):
            assert isinstance(typ, Iter)
            pencode = EncodeCollection(EncodeValue(typ.itemType), identifier)
        else:
            pencode = EncodeValue(typ, identifier)

        return EncodeGet(getterOnDict(identifier), pencode)

    def encodeQuery(self, queryType, getterQuery, encoders, ordering):
        '''
        Processes the query type and provides encoders and ordering encoders for it.
        
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
        assert isinstance(encoders, list), 'Invalid encoders %s' % encoders
        assert isinstance(ordering, dict), 'Invalid ordering %s' % ordering

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

            for prop, propType in criteria.properties.items():
                if prop in exclude: continue
                pencode = self.encodePrimitive(prop, propType)
                encoders.append(EncodeGet(getterOnObjIfIn(prop, ctype.childTypeFor(prop)), pencode))

    # ----------------------------------------------------------------

    def findInvokerModel(self, invoker):
        '''
        Finds out the invoker targeted model.
        
        @param invoker: Invoker
            The invoker to find the model for.
        @return: TypeModel|None
            The found type model or None.
        '''
        assert isinstance(invoker, Invoker), 'Invalid invoker %s' % invoker
        if isinstance(invoker.output, TypeModel): return invoker.output
        elif isinstance(invoker.output, TypeModelProperty): return invoker.output.parent

# --------------------------------------------------------------------

def setterOrdering(getterQuery, entryType):
    '''
    Create a setter specific for the AsOrdered criteria.
    
    @param getterQuery: callable(object)
        The call used for getting the query instance.
    @param entryType: TypeCriteriaEntry
        The criteria entry type of the AsOrdered criteria to manage.
    '''
    assert callable(getterQuery), 'Invalid query getter %s' % getterQuery
    assert isinstance(entryType, TypeCriteriaEntry), 'Invalid entry type %s' % entryType
    assert isinstance(entryType.parent, TypeQuery)

    def setter(obj, value):
        query = getterQuery(obj)
        # We first find the biggest priority in the query
        priority = 0
        for etype in entryType.parent.childTypes():
            assert isinstance(etype, TypeCriteriaEntry)
            if etype == entryType: continue
            if not issubclass(etype.forClass, AsOrdered): continue

            if etype in query:
                criteria = getattr(query, etype.name)
                assert isinstance(criteria, AsOrdered), 'Invalid criteria %s' % criteria
                if AsOrdered.priority in criteria: priority = max(priority, criteria.priority)

        criteria = getattr(query, entryType.name)
        assert isinstance(criteria, AsOrdered), 'Invalid criteria %s' % criteria
        criteria.ascending = value
        criteria.priority = priority + 1
    return setter

class DecodeOrdering(DecodeNode):
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

        invalid = []
        for value in values:
            if not isinstance(value, str): invalid.append(value)
            else:
                if not super().decode(deque(value.split(self.separator)), self.ascending, obj, context):
                    invalid.append(value)

        if invalid: raise DevelError('Cannot order by %s' % invalid)
        return True

# --------------------------------------------------------------------

