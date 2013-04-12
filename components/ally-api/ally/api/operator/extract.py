'''
Created on Mar 16, 2012

@package: ally api
@copyright: 2012 Sourcefabric o.p.s.
@license: http://www.gnu.org/licenses/gpl-3.0.txt
@author: Gabriel Nistor

Provides the configuration functions.
'''

from ..type import Non, Type, Input, Iter, List, typeFor
from .container import Call, Container, Query
from .type import TypeContainer, TypeCriteria, TypeQuery, TypeModelProperty, \
    TypeModel
from ally.exception import DevelError
from ally.support.util import IS_PY3K
from inspect import isfunction, getfullargspec, getargspec
import logging
from ally.api.operator.type import TypeProperty

# --------------------------------------------------------------------

log = logging.getLogger(__name__)

# --------------------------------------------------------------------

def extractProperties(namescape):
    '''
    Extracts the properties from the container class.
    
    @param namescape: dictionary{string, object}
        The class namescape to extract the properties from, usually class.__dict__
    @return: dictionary{string, Type}
        A dictionary containing as a key the property name and as a value the property type.
    '''
    properties = {}
    for name, value in namescape.items():
        if name.startswith('_') or isfunction(value):
            continue
        typ = typeFor(value)
        if typ is None:
            log.warning('Cannot extract property for class %s attribute "%s" of value %s',
                        namescape.get('__name__'), name, value)
        else:
            properties[name] = typ

    return properties

def extractContainersFrom(classes, forType=TypeContainer):
    '''
    Extracts the inherited containers from the container class.
    
    @param classes: tuple(class)|list(class)
        The container class to extract the containers from.
    @param forType: class
        The type of the container to extract the inherited containers from, the type needs to be a subclass of
        TypeContainer.
    @return: list[Container]
        A list of inherited containers in the inherited oreder.
    '''
    assert isinstance(classes, (tuple, list)), 'Invalid classes %s' % classes
    assert issubclass(forType, TypeContainer), 'Invalid for type class %s' % forType

    containers = [typeFor(base) for base in classes]
    containers = [type.container for type in containers if isinstance(type, forType)]

    return containers

def extractPropertiesInherited(classes, forType=TypeContainer):
    '''
    Extracts the inherited properties from the container class.
    
    @param classes: tuple(class)|list(class)
        The container class to extract the inherited properties from.
    @param forType: class
        The type of the container to extract the inherited properties from, the type needs to be a subclass of
        TypeContainer.
    @return: dictionary{string, Type}
        A dictionary containing as a key the property name and as a value the property type.
    '''
    containers = extractContainersFrom(classes, forType)
    containers.reverse() #We reverse since the priority is from first class to last
    properties = {}
    for container in containers:
        assert isinstance(container, Container)
        properties.update(container.properties)
    return properties

# --------------------------------------------------------------------

def extractCriterias(namespace):
    '''
    Extract the criteria's that are found in the provided query class.
    
    @param namespace: dictionary{string, object}
        The query class namespace to extract to extract the criteria's from.
    @return: dictionary{string, class}
        A dictionary containing as the key the criteria name and as a value the criteria class.
    '''
    criterias = {}
    for name, value in namespace.items():
        if name.startswith('_') or isfunction(value):
            continue
        typ = typeFor(value)
        if isinstance(typ, TypeCriteria):
            assert isinstance(typ, TypeCriteria)
            criterias[name] = typ.clazz
        else:
            log.warning('Cannot extract criteria for class %s attribute "%s" of value %s',
                        namespace.get('__name__'), name, value)

    return criterias

def extractCriteriasInherited(classes):
    '''
    Extracts the inherited criteria's from the query class.
    
    @param classes: tuple(class)|list[class]
        The query classes to extract the inherited criteria's from.
    @return: dictionary{string, class}
        A dictionary containing as a key the criteria name and as a value the criteria class.
    '''
    assert isinstance(classes, (tuple, list)), 'Invalid classes %s' % classes

    queries = [typeFor(base) for base in classes]
    queries = [typ.query for typ in queries if isinstance(typ, TypeQuery)]

    queries.reverse() #We reverse since the priority is from first class to last
    criterias = {}
    for query in queries:
        assert isinstance(query, Query)
        criterias.update(query.criterias)
    return criterias

# --------------------------------------------------------------------

def extractOuputInput(function, types=None, modelToId=False):
    '''
    Extracts the input and output for a call based on the provided function.
    
    @param function: function
        The function to extract the call for
    @param types: list[Type or Type container]|None
        The list of types to associate with the function, if they are not provided then the function annotations
        are considered.
    @param modelToId: boolean
        Flag indicating that the extract should convert all inputs that are model types to their actually
        corresponding property type, used in order not to constantly provide the id property of the model when in fact
        we can deduce that the API annotation actually refers to the id and not the model.
    @return: tuple(Type, list[Input])
        A tuple containing on the first position the output type of the call and second the list of inputs for the call.
    '''
    assert isfunction(function), 'Invalid function %s' % function
    assert isinstance(modelToId, bool), 'Invalid model to id flag %s' % modelToId
    if IS_PY3K:
        fnArgs = getfullargspec(function)
        args, varargs, keywords, defaults = fnArgs.args, fnArgs.varargs, fnArgs.varkw, fnArgs.defaults
        annotations = fnArgs.annotations
    else:
        args, varargs, keywords, defaults = getargspec(function)
        annotations = {}

    assert varargs is None, 'No variable arguments are allowed'
    assert keywords is None, 'No keywords arguments are allowed'
    assert 'self' == args[0], 'The call needs to be tagged in a class definition'

    if types:
        assert isinstance(types, (list, tuple)), 'Invalid types list %s' % types
        assert len(args) == len(types), 'The functions parameters are not equal with the provided input types'
        assert not annotations, 'The types for the input arguments cannot be declared as annotations %s and call '\
        'arguments %s' % (annotations, types)
        annotations['return'] = types[0]
        annotations.update({args[k]:types[k] for k in range(1, len(args))})

    mandatory = len(args) - (1 if defaults is None else len(defaults) + 1)
    typ = fnArgs.annotations.get('return')
    output, inputs = typeFor(Non if typ is None else typ), []
    for k, arg in enumerate(args[1:]):
        if arg in args:
            if arg not in annotations: raise DevelError('There is no type for %s' % arg)
            typ = typeFor(annotations[arg])
            assert isinstance(typ, Type), 'Could not obtain a valid type for %s with %s' % (arg, annotations[arg])
            if modelToId and isinstance(typ, TypeModel):
                assert isinstance(typ, TypeModel)
                typ = typ.propertyTypeId()
            if k < mandatory: inputs.append(Input(arg, typ))
            else: inputs.append(Input(arg, typ, True, defaults[k - mandatory]))

    return output, inputs

def processGenericCall(call, generic):
    '''
    If either the output or input of the call is based on the provided super model or query then it will create 
    new call that will have the super model or query replaced with the new model or query in the types of the call.
    
    @param call: Call
        The call to be analyzed.
    @param generic: dictionary{class, class}
        The dictionary containing as a key the class to be generically replaced and as a value the class to replace with.
    @return: Call
        If the provided call is not depended on the super model it will be returned as it is, if not a new call
        will be created with all the dependencies from super model replaced with the new model.
    '''
    assert isinstance(call, Call), 'Invalid call %s' % call
    assert isinstance(generic, dict), 'Invalid generic %s' % generic
    updated = False
    output = processGenericType(call.output, generic)
    if output: updated = True
    else: output = call.output
    inputs = []
    for inp in call.inputs:
        assert isinstance(inp, Input)
        genericType = processGenericType(inp.type, generic)
        if genericType:
            inputs.append(Input(inp.name, genericType, inp.hasDefault, inp.default))
            updated = True
        else: inputs.append(inp)
    if updated:
        newCall = Call(call.name, call.method, output, inputs, call.hints)
        log.info('Generic call transformation from %s to %s' % (call, newCall))
        call = newCall
    return call

def processGenericType(forType, generic):
    '''
    Processes the type if is the case into a new type that is extended from the original but having the new
    model or query as reference instead of the super model or query.
    @see: processCallGeneric
    
    @param forType: Type
        The type to process.
    @param generic: dictionary{class, class}
        The dictionary containing as a key the class to be generically replaced and as a value the class to replace with.
    @return: Type|None
        If the provided type was containing references to the super model than it will return a new type
        with the super model references changes to the new model, otherwise returns None.
    '''
    assert isinstance(forType, Type), 'Invalid type %s' % type
    assert isinstance(generic, dict), 'Invalid generic %s' % generic
    newType = None
    if isinstance(forType, TypeProperty):
        assert isinstance(forType, TypeModelProperty), 'Only allowed model type properties, got %s' % forType
        assert isinstance(forType.parent, TypeContainer)
        genericModelClass = generic.get(forType.parent.clazz)
        if genericModelClass is not None:
            newModelType = typeFor(genericModelClass)
            assert newModelType is not None, 'Invalid generic model class %s, has no model type' % genericModelClass
            newType = TypeModelProperty(newModelType, forType.property, forType.type)
    elif isinstance(forType, TypeModel):
        assert isinstance(forType, TypeModel)
        genericModelClass = generic.get(forType.clazz)
        if genericModelClass is not None:
            newType = typeFor(genericModelClass)
            assert newType is not None, 'Invalid generic model class %s, has no model type' % newType
    elif isinstance(forType, TypeQuery):
        assert isinstance(forType, TypeQuery)
        genericQueryClass = generic.get(forType.clazz)
        if genericQueryClass is not None:
            newType = typeFor(genericQueryClass)
            assert newType is not None, 'Invalid generic query class %s, has no query type' % newType
    elif isinstance(forType, Iter):
        assert isinstance(forType, Iter)
        itemType = processGenericType(forType.itemType, generic)
        if itemType:
            if isinstance(forType, List): newType = List(itemType)
            else: newType = Iter(itemType)
    return newType
