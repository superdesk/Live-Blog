'''
Created on Jul 4, 2011

@package: Newscoop
@copyright: 2011 Sourcefabric o.p.s.
@license: http://www.gnu.org/licenses/gpl-3.0.txt
@author: Gabriel Nistor

Provides the parameters decoders.
'''

from ally.api import configure
from ally.api.criteria import AsOrdered, AsLike
from ally.api.operator import Query, CriteriaEntry, Criteria, Property
from ally.api.type import Input, Iter, Type, TypeQuery
from ally.container.ioc import injected
from ally.core.spec.resources import ConverterPath
from ally.core.spec.server import EncoderParams, DecoderParams
from ally.exception import DevelException
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
        if not valid:
            return False
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
        if not valid:
            return
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
        if not valid:
            return
        typ, isList = valid
        name = self.converterPath.normalize(inp.name)
        values = extractParamValues(params, name)
        if len(values) > 1:
            if not isList:
                raise DevelException('Parameter %r needs to be provided just once' % name)
            vals = []
            for value in values:
                try:
                    vals.append(self.converterPath.asValue(value, typ))
                except ValueError:
                    raise DevelException('Invalid value %r for parameter %r, expected type %s' % (value, name, typ))
            args[inp.name] = vals
        elif len(values) == 1:
            value = values[0]
            if value != '':
                try:
                    arg = self.converterPath.asValue(value, typ)
                except ValueError:
                    raise DevelException('Invalid value %r for parameter %r, expected type %s' % (value, name, typ))
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
        query = self._validate(inp)
        if not query:
            return 
        groupByProp = _groupCriteriaEntriesByProperty(query)
        #TODO: optimize, this processing's can be split into processing classes latter one as an example
        # we could have a OrderCriteriaHandler based on a generic criteria handler API.
        for prop, crtEntrs in groupByProp:
            if prop.name == 'orderAscending' and issubclass(crtEntrs[0].criteria.criteriaClass, AsOrdered):
                self._encodeOrdering(prop, crtEntrs, inputs, query=arg, params=params)
            else:
                self._encodeSimple(prop, crtEntrs, inputs, query=arg, params=params)
    
    def encodeModels(self, inputs, inp, models):
        '''
        @see: EncoderParams.encodeModels
        '''
        query = self._validate(inp)
        if not query:
            return 
        groupByProp = _groupCriteriaEntriesByProperty(query)
        for prop, crtEntrs in groupByProp:
            if prop.name == 'orderAscending' and issubclass(crtEntrs[0].criteria.criteriaClass, AsOrdered):
                self._encodeOrdering(prop, crtEntrs, inputs, models=models)
            elif prop.name == 'like' and issubclass(crtEntrs[0].criteria.criteriaClass, AsLike):
                self._encodeSimple(prop, crtEntrs, inputs, models=models, modelNone='')
            else:
                self._encodeSimple(prop, crtEntrs, inputs, models=models)
    
    def decode(self, inputs, inp, params, args):
        '''
        @see: DecoderParams.decode
        '''
        assert isinstance(inp, Input), 'Invalid input %s' % inp
        assert isinstance(params, list), 'Invalid parameters list %s' % params
        assert isinstance(args, dict), 'Invalid arguments dictionary %s' % args
        query = self._validate(inp)
        if not query:
            return
        assert isinstance(query, Query)
        groupByProp = _groupCriteriaEntriesByProperty(query)
        q = None
        for prop, crtEntrs in groupByProp:
            if prop.name == 'orderAscending' and issubclass(crtEntrs[0].criteria.criteriaClass, AsOrdered):
                q = self._decodeOrdering(prop, crtEntrs, inputs, query, q, params)
            else:
                q = self._decodeSimple(prop, crtEntrs, inputs, query, q, params)
        if q is not None:
            args[inp.name] = q
    
    def _validate(self, inp):
        assert isinstance(inp, Input)
        typ = inp.type
        if isinstance(typ, TypeQuery):
            assert isinstance(typ, TypeQuery)
            return typ.query
        return False
    
    def _encodeOrdering(self, prop, criteriaEntries, inputs, query=None, params=None, models=None):
        assert isinstance(prop, Property)
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
            names = [crtEnt.name for crtEnt in criteriaEntries]
            models[nameAsc] = (True, str, names)
            models[nameDesc] = (True, str, names)
        if params is not None:
            assert isinstance(params, list)
            ordered = {}
            for crtEnt in criteriaEntries:
                assert isinstance(crtEnt, CriteriaEntry)
                crit = crtEnt.get(query)
                if crit is not None:
                    assert isinstance(crit, AsOrdered)
                    asc = prop.get(crit)
                    if asc is not None:
                        ordered[crit.index()] = (asc, crtEnt.name)
                for key in sorted(ordered.keys()):
                    asc, name = ordered[key]
                    if asc:
                        params.append((nameAsc, name))
                    else:
                        params.append((nameDesc, name))

    def _encodeSimple(self, prop, criteriaEntries, inputs, query=None, params=None, models=None, modelNone=None):
        assert isinstance(prop, Property)
        assert not isinstance(prop.type, Iter), \
        'WTF, cannot encode list properties, the query supposed to have only primitives as properties'
        if prop.name in configure.DEFAULT_CONDITIONS:
            names = (prop.name + self.separatorName + crtEnt.name if _isNameInPrimitives(inputs, crtEnt.name) else \
                     crtEnt.name for crtEnt in criteriaEntries)
        else:
            names = (crtEnt.name for crtEnt in criteriaEntries)
        for name, crtEnt in zip(names, criteriaEntries):
            assert isinstance(crtEnt, CriteriaEntry)
            name = self.converterPath.normalize(name)
            if models is not None:
                assert isinstance(models, dict)
                assert not name in models, 'There is already a model with name (%s)' % name
                models[name] = (False, prop.type.forClass, modelNone)
            if params is not None:
                assert isinstance(params, list)
                crit = crtEnt.get(query)
                if crit is not None:
                    value = prop.get(crit)
                    if value is not None:
                        params.append((name, self.converterPath.asString(value)))
    
    def _decodeOrdering(self, prop, criteriaEntries, inputs, query, q, params):
        assert isinstance(prop, Property)
        assert isinstance(query, Query)
        assert isinstance(params, list)
        assert not _isNameInPrimitives(inputs, self.nameOrderAsc), \
        'The primitive inputs %s contain a variable called (%s)' % (inputs, self.nameOrderAsc)
        assert not _isNameInPrimitives(inputs, self.nameOrderDesc), \
        'The primitive inputs %s contain a variable called (%s)' % (inputs, self.nameOrderDesc)
        nameAsc = self.converterPath.normalize(self.nameOrderAsc)
        orderParams = extractParams(params, nameAsc, self.converterPath.normalize(self.nameOrderDesc))
        for param in orderParams:
            order, name = param
            crtEnt = _findCriteriaEntryByName(criteriaEntries, name)
            if not crtEnt: params.append(param);
            else:
                assert isinstance(crtEnt, CriteriaEntry)
                if q is None:
                    q = query.createQuery()
                crit = crtEnt.obtain(q)
                prop.set(crit, order == nameAsc)
        return q
    
    def _decodeSimple(self, prop, criteriaEntries, inputs, query, q, params):
        assert isinstance(prop, Property)
        assert not isinstance(prop.type, Iter), \
        'WTF, cannot encode list properties, the query supposed to have only primitives as properties'
        assert isinstance(params, list)
        if prop.name in configure.DEFAULT_CONDITIONS:
            names = [prop.name + self.separatorName + crtEnt.name if _isNameInPrimitives(inputs, crtEnt.name) else \
                     crtEnt.name for crtEnt in criteriaEntries]
        else:
            names = [prop.name + self.separatorName + crtEnt.name for crtEnt in criteriaEntries]
        for name, crtEnt in zip(names, criteriaEntries):
            assert isinstance(crtEnt, CriteriaEntry)
            name = self.converterPath.normalize(name)
            values = extractParamValues(params, name)
            if len(values) > 1:
                raise DevelException('Parameter %r needs to be provided just once' % name)
            elif len(values) == 1:
                if q is None:
                    q = query.createQuery()
                crit = crtEnt.obtain(q)
                prop.set(crit, self.converterPath.asValue(values[0], prop.type))
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

def _groupCriteriaEntriesByProperty(query):
    '''
    FOR INTERNAL USE.
    Groups the query criteria entries based on properties, so if there are multiple criteria entries in a query
    that have the same property than this will grouped them based on that.
    '''
    assert isinstance(query, Query)
    #TODO: maybe cache the grouped structure
    groupByProp = []
    for crtEnt in query.criteriaEntries.values():
        assert isinstance(crtEnt, CriteriaEntry)
        crt = crtEnt.criteria
        assert isinstance(crt, Criteria)
        for prop in crt.properties.values():
            assert isinstance(prop, Property)
            found = False
            for gr in groupByProp:
                if gr[0] == prop:
                    gr[1].append(crtEnt)
                    found = True
                    break
            if not found:
                groupByProp.append((prop, [crtEnt]))
    return groupByProp

def _findCriteriaEntryByName(criteriaEntries, name):
    '''
    FOR INTERNAL USE.
    Finds the criteria name with the specified name.
    '''
    for crtEnt in criteriaEntries:
        assert isinstance(crtEnt, CriteriaEntry)
        if crtEnt.name == name:
            return crtEnt
