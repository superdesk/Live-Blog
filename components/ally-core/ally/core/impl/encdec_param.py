'''
Created on Jul 4, 2011

@package: ally core
@copyright: 2012 Sourcefabric o.p.s.
@license: http://www.gnu.org/licenses/gpl-3.0.txt
@author: Gabriel Nistor

Provides the parameters decoders.
'''

from ally.api.criteria import AsOrdered, AsLike
from ally.api.operator.type import TypeQuery, TypeCriteriaEntry, TypeProperty
from ally.api.type import Input, Iter, Type, typeFor
from ally.container.ioc import injected
from ally.core.spec.resources import ConverterPath
from ally.core.spec.server import EncoderParams, DecoderParams
from ally.exception import DevelError
from ally.support.core.util_param import extractParamValues, extractParams, \
    containsParam

# --------------------------------------------------------------------

@injected
class EncDecPrimitives(EncoderParams, DecoderParams):
    '''
    Provides the parameters encoding and decoding based on inputs that are primitives or list of primitives.
    @see: EncoderParams, DecoderParams
    '''

    converterPath = ConverterPath
    # The converter path used in parsing the parameter values.

    def __init__(self):
        assert isinstance(self.converterPath, ConverterPath), 'Invalid ConverterPath object %s' % self.converterPath

    def encode(self, inputs, inp, arg, params):
        '''
        @see: EncoderParams.encode
        '''
        assert isinstance(inp, Input), 'Invalid input %s' % inp
        assert isinstance(params, list), 'Invalid parameters list %s' % params
        assert arg is not None, 'Provide an argument value'
        valid = self._validate(inp)
        if not valid: return False

        isList = valid[1]
        name = self.converterPath.normalize(inp.name)
        assert not containsParam(params, name), 'There is already a parameter with name %s' % name
        if isList:
            for item in arg:
                params.append((name, self.converterPath.asString(item)))
        else:
            params.append((name, self.converterPath.asString(arg)))
        return True

    def encodeModels(self, inputs, inp, models):
        '''
        @see: EncoderParams.encodeModels
        '''
        assert isinstance(inp, Input), 'Invalid input %s' % inp
        assert isinstance(models, dict), 'Invalid models dictionary %s' % models
        valid = self._validate(inp)
        if not valid: return

        typ, isList = valid
        name = self.converterPath.normalize(inp.name)
        assert not name in models, 'There is already a model with name %s' % name
        models[name] = (isList, typ, None)

    def decode(self, inputs, inp, params, args):
        '''
        @see: DecoderParams.decode
        '''
        assert isinstance(inp, Input), 'Invalid input %s' % inp
        assert isinstance(params, list), 'Invalid parameters list %s' % params
        assert isinstance(args, dict), 'Invalid arguments dictionary %s' % args
        valid = self._validate(inp)
        if not valid: return

        typ, isList = valid
        name = self.converterPath.normalize(inp.name)
        values = extractParamValues(params, name)
        if len(values) > 1:
            if not isList:
                raise DevelError('Parameter %r needs to be provided just once' % name)
            vals = []
            for value in values:
                try:
                    vals.append(self.converterPath.asValue(value, typ))
                except ValueError:
                    raise DevelError('Invalid value %r for parameter %r, expected type %s' % (value, name, typ))
            args[inp.name] = vals
        elif len(values) == 1:
            value = values[0]
            if value != '':
                try:
                    arg = self.converterPath.asValue(value, typ)
                except ValueError:
                    raise DevelError('Invalid value %r for parameter %r, expected type %s' % (value, name, typ))
                if isList:
                    args[inp.name] = [arg]
                else:
                    args[inp.name] = arg

    def _validate(self, inp):
        assert isinstance(inp, Input)
        typ = inp.type
        isList = False
        # Need to check if is not a list.
        if isinstance(typ, Iter):
            typ = typ.itemType
            isList = True
        assert isinstance(typ, Type)
        if not typ.isPrimitive:
            return False
        return (typ, isList)

@injected
class EncDecQuery(EncoderParams, DecoderParams):
    '''
    Provides the query encoding and decoding based on query inputs.
    @attention: You should always place the encoder/decoder of queries after the primitives since this will relay on
    existing parameters to deduce the encoding/decoding.
    @see: EncoderParams, DecoderParams 
    '''

    converterPath = ConverterPath
    # The converter path used in parsing the parameter values.
    nameOrderAsc = 'asc'
    nameOrderDesc = 'desc'
    separatorName = '.'
    # The separator used in extending parameters from names.

    def __init__(self):
        assert isinstance(self.converterPath, ConverterPath), 'Invalid ConverterPath object %s' % self.converterPath
        assert isinstance(self.nameOrderAsc, str), 'Invalid string %s' % self.nameOrderAsc
        assert isinstance(self.nameOrderDesc, str), 'Invalid string %s' % self.nameOrderDesc
        assert isinstance(self.separatorName, str), 'Invalid string %s' % self.separatorName

    def encode(self, inputs, inp, arg, params):
        '''
        @see: EncoderParams.encode
        '''
        assert isinstance(inp, Input), 'Invalid input %s' % inp
        assert isinstance(params, list), 'Invalid parameters list %s' % params
        assert arg is not None, 'Provide an argument value'
        queryType = self._validate(inp)
        if not queryType: return

        groupByProp = _groupCriteriaEntriesByProperty(queryType)
        #TODO: optimize, this processing's can be split into processing classes latter one as an example
        # we could have a OrderCriteriaHandler based on a generic criteria handler API.
        for propType, criteriaEntriesTypes in groupByProp:
            assert isinstance(propType, TypeProperty)
            if propType.property == 'ascending' and issubclass(criteriaEntriesTypes[0].forClass, AsOrdered):
                self._encodeOrdering(propType, criteriaEntriesTypes, inputs, query=arg, params=params)
            else:
                self._encodeSimple(propType, criteriaEntriesTypes, inputs, query=arg, params=params)

    def encodeModels(self, inputs, inp, models):
        '''
        @see: EncoderParams.encodeModels
        '''
        queryType = self._validate(inp)
        if not queryType: return

        groupByProp = _groupCriteriaEntriesByProperty(queryType)
        for propType, criteriaEntriesTypes in groupByProp:
            assert isinstance(propType, TypeProperty)
            if propType.property == 'ascending' and issubclass(criteriaEntriesTypes[0].forClass, AsOrdered):
                self._encodeOrdering(propType, criteriaEntriesTypes, inputs, models=models)
            elif propType.property == 'like' and issubclass(criteriaEntriesTypes[0].forClass, AsLike):
                self._encodeSimple(propType, criteriaEntriesTypes, inputs, models=models, modelNone='')
            else:
                self._encodeSimple(propType, criteriaEntriesTypes, inputs, models=models)

    def decode(self, inputs, inp, params, args):
        '''
        @see: DecoderParams.decode
        '''
        assert isinstance(inp, Input), 'Invalid input %s' % inp
        assert isinstance(params, list), 'Invalid parameters list %s' % params
        assert isinstance(args, dict), 'Invalid arguments dictionary %s' % args
        queryType = self._validate(inp)
        if not queryType: return

        groupByProp = _groupCriteriaEntriesByProperty(queryType)
        q = None
        for propType, criteriaEntriesTypes in groupByProp.items():
            assert isinstance(propType, TypeProperty)
            if propType.property == 'ascending' and issubclass(criteriaEntriesTypes[0].forClass, AsOrdered):
                q = self._decodeOrdering(propType, criteriaEntriesTypes, inputs, queryType, q, params)
            else:
                q = self._decodeSimple(propType, criteriaEntriesTypes, inputs, queryType, q, params)
        if q is not None:
            args[inp.name] = q

    def _validate(self, inp):
        assert isinstance(inp, Input)
        if isinstance(inp.type, TypeQuery): return inp.type
        return False

    def _encodeOrdering(self, propType, criteriaEntriesTypes, inputs, query=None, params=None, models=None):
        assert isinstance(propType, TypeProperty)
        assert not _isNameInPrimitives(inputs, self.nameOrderAsc), \
        'The primitive inputs %s contain a variable called (%s)' % (inputs, self.nameOrderAsc)
        assert not _isNameInPrimitives(inputs, self.nameOrderDesc), \
        'The primitive inputs %s contain a variable called (%s)' % (inputs, self.nameOrderDesc)
        nameAsc = self.converterPath.normalize(self.nameOrderAsc)
        nameDesc = self.converterPath.normalize(self.nameOrderDesc)
        if models is not None:
            assert isinstance(models, dict)
            assert not nameAsc in models, 'There is already a model with name (%s)' % nameAsc
            assert not nameDesc in models, 'There is already a model with name (%s)' % nameDesc
            names = [crtEntType.criteria for crtEntType in criteriaEntriesTypes]
            models[nameAsc] = (True, str, names)
            models[nameDesc] = (True, str, names)
        if params is not None:
            assert isinstance(params, list)
            ordered, unordered = {}, []
            for crtEntType in criteriaEntriesTypes:
                assert isinstance(crtEntType, TypeCriteriaEntry)
                if crtEntType in query:
                    crit = getattr(query, crtEntType.name)
                    assert isinstance(crit, AsOrdered)
                    asc = getattr(crit, propType.property)
                    if asc is not None:
                        if crit.priority:
                            l = ordered.get(crit.priority)
                            if not l: ordered[crit.priority] = [(asc, crtEntType.name)]
                            else: l.append((asc, crtEntType.name))
                        else:
                            unordered.append((asc, crtEntType.name))
                inorder = []
                for priority in sorted(ordered.keys()):
                    inorder.extend(ordered[priority])
                inorder.extend(unordered)
                for asc, name in inorder:
                    if asc: params.append((nameAsc, name))
                    else: params.append((nameDesc, name))

    def _encodeSimple(self, propType, criteriaEntriesTypes, inputs, query=None, params=None, models=None, modelNone=None):
        assert isinstance(propType, TypeProperty)
        assert not isinstance(propType.type, Iter), \
        'WTF, cannot encode list properties, the query supposed to have only primitives as properties'
        defaults = [crtEntrType.criteria.main for crtEntrType in criteriaEntriesTypes]
        if propType.property in defaults:
            names = (propType.property + self.separatorName + crtEntrType.name
                     if _isNameInPrimitives(inputs, crtEntrType.name)
                     else crtEntrType.name for crtEntrType in criteriaEntriesTypes)
        else:
            names = (propType.property + crtEntrType.name for crtEntrType in criteriaEntriesTypes)
        for name, crtEntrType in zip(names, criteriaEntriesTypes):
            assert isinstance(crtEntrType, TypeCriteriaEntry)
            name = self.converterPath.normalize(name)
            if models is not None:
                assert isinstance(models, dict)
                assert not name in models, 'There is already a model with name (%s)' % name
                models[name] = (False, propType.type.forClass, modelNone)
            if params is not None:
                assert isinstance(params, list)
                crit = getattr(query, crtEntrType.name)
                if crit is not None:
                    value = getattr(crit, propType.property)
                    if value is not None:
                        params.append((name, self.converterPath.asString(value)))

    def _decodeOrdering(self, propType, criteriaEntriesTypes, inputs, queryType, q, params):
        assert isinstance(propType, TypeProperty)
        assert isinstance(queryType, TypeQuery)
        assert isinstance(params, list)
        assert not _isNameInPrimitives(inputs, self.nameOrderAsc), \
        'The primitive inputs %s contain a variable called (%s)' % (inputs, self.nameOrderAsc)
        assert not _isNameInPrimitives(inputs, self.nameOrderDesc), \
        'The primitive inputs %s contain a variable called (%s)' % (inputs, self.nameOrderDesc)
        nameAsc = self.converterPath.normalize(self.nameOrderAsc)
        orderParams = extractParams(params, nameAsc, self.converterPath.normalize(self.nameOrderDesc))
        priority = 1
        for param in orderParams:
            order, name = param
            crtEntrType = _findCriteriaEntryByName(criteriaEntriesTypes, name)
            if not crtEntrType: params.append(param);
            else:
                assert isinstance(crtEntrType, TypeCriteriaEntry)
                if q is None: q = queryType.forClass()
                crit = getattr(q, crtEntrType.name)
                setattr(crit, propType.property, order == nameAsc)
                setattr(crit, 'priority', priority)
                priority += 1
        return q

    def _decodeSimple(self, propType, criteriaEntriesTypes, inputs, queryType, q, params):
        assert isinstance(propType, TypeProperty)
        assert isinstance(queryType, TypeQuery)
        assert not isinstance(propType.type, Iter), \
        'WTF, cannot encode list properties, the query supposed to have only primitives as properties'
        assert isinstance(params, list)
        defaults = [crtEntrType.criteria.main for crtEntrType in criteriaEntriesTypes]
        if propType.property in defaults:
            names = [propType.property + self.separatorName + crtEntrType.name
                     if _isNameInPrimitives(inputs, crtEntrType.name)
                     else crtEntrType.name for crtEntrType in criteriaEntriesTypes]
        else:
            names = [propType.property + self.separatorName + crtEntrType.name for crtEntrType in criteriaEntriesTypes]
        for name, crtEntrType in zip(names, criteriaEntriesTypes):
            assert isinstance(crtEntrType, TypeCriteriaEntry)
            name = self.converterPath.normalize(name)
            values = extractParamValues(params, name)
            if len(values) > 1:
                raise DevelError('Parameter %r needs to be provided just once' % name)
            elif len(values) == 1:
                if q is None: q = queryType.forClass()
                crit = getattr(q, crtEntrType.name)
                setattr(crit, propType.property, self.converterPath.asValue(values[0], propType.type))
        return q

# --------------------------------------------------------------------

def _isNameInPrimitives(inputs, name):
    '''
    FOR INTERNAL USE.
    Checks  if the name is in the provided primitive type inputs.
    '''
    for inp in inputs:
        assert isinstance(inp, Input)
        if inp.type.isPrimitive and inp.name == name:
            return True
    return False

def _groupCriteriaEntriesByProperty(queryType):
    '''
    FOR INTERNAL USE.
    Groups the query criterias based on properties, so if there are multiple criteria entries in a query that have the
    same property then this will grouped them based on that.
    
    @param query: Query
        The query to extract the grouping for.
    @return: dictionary{TypeProperty, list[TypeCriteriaEntry]}
        The groupings.
    '''
    assert isinstance(queryType, TypeQuery)
    #TODO: maybe cache the grouped structure
    groupByProp = {}
    for criteria in queryType.query.criterias:
        crtEntryType = typeFor(getattr(queryType.forClass, criteria))
        assert isinstance(crtEntryType, TypeCriteriaEntry)
        for prop in crtEntryType.criteria.properties:
            propType = typeFor(getattr(crtEntryType.forClass, prop))
            crtEntriesTypes = groupByProp.get(propType)
            if crtEntriesTypes is None: groupByProp[propType] = [crtEntryType]
            else: crtEntriesTypes.append(crtEntryType)
    return groupByProp

def _findCriteriaEntryByName(criteriaEntriesTypes, name):
    '''
    FOR INTERNAL USE.
    Finds the criteria name with the specified name.
    '''
    for crtEntrType in criteriaEntriesTypes:
        assert isinstance(crtEntrType, TypeCriteriaEntry)
        if crtEntrType.name == name:
            return crtEntrType
