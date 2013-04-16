'''
Created on May 29, 2011

@package: ally api
@copyright: 2012 Sourcefabric o.p.s.
@license: http://www.gnu.org/licenses/gpl-3.0.txt
@author: Gabriel Nistor

Provides the operator containers that describe the APIs.
'''

from ..type import Type, Input
from inspect import isclass

# --------------------------------------------------------------------

class Container:
    '''
    Container for properties.
    '''

    __slots__ = ('properties',)

    def __init__(self, properties):
        '''
        Create the properties container.
        
        @param properties: dictionary{string, Type}
            A dictionary containing as a key the property name and as a value the property type.
        '''
        assert isinstance(properties, dict), 'The properties %s need to be a dictionary' % properties
        if __debug__:
            for typName, typ in properties.items():
                assert isinstance(typName, str), 'Invalid type name %s' % typName
                assert isinstance(typ, Type), 'Not a criteria type %s' % typ

        self.properties = properties

    def __str__(self):
        return '<%s %s>' % (self.__class__.__name__, [str(prop) for prop in self.properties])

class Model(Container):
    '''
    Contains the data for an API model mapping.
    '''

    __slots__ = ('propertyId', 'name', 'hints')

    def __init__(self, properties, name, propertyId=None, hints={}):
        '''
        Constructs a properties model.
        @see: Container.__init__
        
        @param name: string
            The name of the model.
        @param propertyId: string|None
            The property that represent the id of the model, if None then it means the model doesn't poses an id.
        @param hints: dictionary{string, object}
            The hints associated with the model.
        '''
        Container.__init__(self, properties)

        assert isinstance(name, str) and len(name) > 0, 'Invalid model name %s' % name
        assert propertyId is None or isinstance(propertyId, str) and propertyId in properties, \
        'Invalid id property %s' % propertyId
        assert isinstance(hints, dict), 'Invalid hints %s' % hints
        if __debug__:
            for hintn in hints: assert isinstance(hintn, str), 'Invalid hint name %s' % hintn

        self.name = name
        self.propertyId = propertyId
        self.hints = hints

    def __hash__(self):
        return hash(self.name)

    def __eq__(self, other):
        if isinstance(other, self.__class__): return self.name == other.name
        return False

    def __str__(self):
        return '<%s %s>' % (self.name, [str(prop) for prop in self.properties])

class Criteria(Container):
    '''
    Used for mapping the API criteria.
    @attention: The criteria will allow only for primitive types.
    '''

    __slots__ = ('main',)

    def __init__(self, properties, main=()):
        '''
        Create the criteria with the provided properties, is very similar to a Model.
        @see: Container.__init__
        
        @param main: list[string]|tuple(string)
            The main properties for the criteria, the main is used whenever a value is set directly on the 
            criteria. The main properties needs to be found in the provided properties and have compatible types.
        '''
        assert isinstance(main, (list, tuple)), 'Invalid main properties %s' % main
        if __debug__:
            for typ in properties.values():
                assert isinstance(typ, Type), 'Not a criteria type %s' % typ
                assert typ.isPrimitive, 'Not a primitive criteria type for %s' % typ
            typ = None
            for prop in main:
                assert prop in properties, \
                'Invalid main property %s, is not found in the provided properties' % prop
                if typ is not None:
                    assert properties[prop].isOf(typ), \
                    'Invalid main property %s with type %s' % (prop, properties[prop])
                else: typ = properties[prop]

        Container.__init__(self, properties)

        self.main = tuple(main)

class Query:
    '''
    Used for mapping the API query.
    '''

    __slots__ = ('criterias',)

    def __init__(self, criterias):
        '''
        Initialize the criteria's of this query.
        
        @param criterias: dictionary{string, class}
            The criteria's dictionary that belong to this query, as a key is the criteria name (how is been 
            declared in the query) and as a value the criteria class.
        '''
        assert isinstance(criterias, dict), 'The criterias %s need to be a dictionary' % criterias
        if __debug__:
            for crtName, crtClass in criterias.items():
                assert isinstance(crtName, str), 'Invalid criteria name %s' % crtName
                assert isclass(crtClass), 'Not a criteria class %s' % crtClass

        self.criterias = criterias

    def __str__(self):
        return '<Query %s>' % [str(entry) for entry in self.criterias]

# --------------------------------------------------------------------

class Call:
    '''
    Provides the container for a service call. This class will basically contain all the types that are involved in
    input and output from the call.
    '''

    __slots__ = ('name', 'method', 'output', 'inputs', 'hints', 'mandatory')

    def __init__(self, name, method, output, inputs, hints={}):
        '''
        Constructs an API call that will have the provided input and output types.
        
        @param name: string
            The name of the function represented by the call.
        @param method: integer
            The method of the call, can be one of GET, INSERT, UPDATE or DELETE constants in this module.
        @param output: Type
            The output type for the service call.
        @param inputs: list[Input]|tuple(Input)
            A list containing all the Input's of the call.
        @param hints: dictionary{string, object}
            The hints associated with the call.
        @ivar mandatory: integer
            Provides the count of the mandatory input types, if the mandatory count is two and we have three input
            types it means that just the first two parameters need to be provided.
        '''
        assert isinstance(name, str) and name.strip(), 'Provide a valid name'
        assert isinstance(method, int), 'Invalid method %s' % method
        assert isinstance(output, Type), 'Invalid output type %s' % output
        assert isinstance(inputs, (list, tuple)), 'Invalid inputs %s, needs to be a list' % inputs
        assert isinstance(hints, dict), 'Invalid hints %s' % hints
        if __debug__:
            for hintn in hints: assert isinstance(hintn, str), 'Invalid hint name %s' % hintn

        mandatory = 0
        for inp in inputs:
            assert isinstance(inp, Input), 'Not an input %s' % input
            if inp.hasDefault: break
            mandatory += 1

        self.name = name
        self.method = method
        self.output = output
        self.inputs = tuple(inputs)
        self.hints = hints
        self.mandatory = mandatory

    def __str__(self):
        inputs = [''.join(('defaulted:' if inp.hasDefault else '', inp.name, '=', str(inp.type))) for inp in self.inputs]
        return '<Call: %s %s(%s))>' % (self.output, self.name, ', '.join(inputs))

class Service:
    '''
    Used for mapping the API calls.
    '''

    __slots__ = ('calls',)

    def __init__(self, calls):
        '''
        Constructs the API service class based on the provided implementation.
        
        @param calls: list[Call]|tuple(Call)
            The calls list that belong to this service class.
        '''
        assert isinstance(calls, (list, tuple)), 'Invalid calls %s, needs to be a list' % calls
        if __debug__:
            for call in calls:
                assert isinstance(call, Call), 'Invalid call %s' % call
        self.calls = {call.name:call for call in calls}

    def __str__(self):
        return '<Service %s>' % [name for name in self.calls]
