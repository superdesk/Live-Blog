'''
Created on Jan 19, 2013

@package: support acl
@copyright: 2012 Sourcefabric o.p.s.
@license: http://www.gnu.org/licenses/gpl-3.0.txt
@author: Gabriel Nistor

Provides the ACL right that is designed for handling service based mapping.
'''

from .spec import RightAcl, Filter
from ally.api.config import GET, INSERT, UPDATE, DELETE
from ally.api.operator.container import Service, Call
from ally.api.operator.type import TypeService
from ally.api.type import typeFor
from ally.support.util import iterRef
from inspect import isfunction

# --------------------------------------------------------------------

class RightService(RightAcl):
    '''
    The ACL right implementation designed for services.
    
    The filter policy is as follows:
        - if a call within a right has multiple representation and there is a filter for that call then only the call
          representation that can be filtered will be used.
        - if a call has a filter defined and is used in conjunction with a different right that doesn't have a filter for
          the same call then the unfiltered call is used, this way the right that allows more access wins.
    '''
    
    def __init__(self, name, description):
        '''
        @see: RightAcl.__init__
        '''
        super().__init__(name, description)
        self.structure = StructureRight()
    
    # ----------------------------------------------------------------
    
    def add(self, *references, filter=None):
        '''
        Used for adding to the right the service calls.
        
        @param references: arguments[tuple(class, string)]
            The references of the service call to associate with the right.
        @param filter: Filter|None
            The filter to be used with the added calls, for more details about filter policy.
        @return: self
            The self object for chaining purposes.
        '''
        indexed = iterRef(references)
        assert indexed, 'At least one reference is required'
        for service, names in indexed.items():
            typ = typeFor(service)
            assert isinstance(typ, TypeService), 'Invalid service %s' % service
            assert isinstance(typ.service, Service)
            for name in names:
                if isfunction(name): name = name.__name__
                assert name in typ.service.calls, 'Invalid call name \'%s\' for service %s' % (name, typ)
                call = typ.service.calls[name]
                assert isinstance(call, Call)
                structCall = self.structure.obtainCall(typ, call)
                if filter: structCall.pushFilter(filter)
        return self
        
    def allFor(self, method, *services, filter=None):
        '''
        Used for adding to the right the service calls that have the specified method.
        
        @param method: integer
            The method or methods composed by using the | operator to be associated with the right.
        @param service: arguments[service type]
            The services types to be used.
        @param filter: Filter|None
            The filter to be used with the added services, for more details about filter policy.
        @return: self
            The self object for chaining purposes.
        '''
        assert isinstance(method, int), 'Invalid method %s' % method
        assert services, 'At least one service is required'
        
        for service in services:
            typ = typeFor(service)
            assert isinstance(typ, TypeService), 'Invalid service %s' % service
            
            assert isinstance(typ.service, Service)
            for call in typ.service.calls.values():
                assert isinstance(call, Call)
                if call.method & method:
                    structCall = self.structure.obtainCall(typ, call)
                    if filter: structCall.pushFilter(filter)
        return self
                    
    def allGet(self, *services, filter=None):
        '''
        Used for adding to the right the service calls that are Get.
        
        @param service: arguments[service type]
            The services types to be used.
        @param filter: Filter|None
            The filter to be used with the added services, for more details about filter policy.
        @return: self
            The self object for chaining purposes.
        '''
        return self.allFor(GET, *services, filter=filter)
        
    def allInsert(self, *services, filter=None):
        '''
        Used for adding to the right the service calls that are Insert.
        
        @param service: arguments[service type]
            The services types to be used.
        @param filter: Filter|None
            The filter to be used with the added services, for more details about filter policy.
        @return: self
            The self object for chaining purposes.
        '''
        return self.allFor(INSERT, *services, filter=filter)
        
    def allUpdate(self, *services, filter=None):
        '''
        Used for adding to the right the service calls that are Update.
        
        @param service: arguments[service type]
            The services types to be used.
        @param filter: Filter|None
            The filter to be used with the added services, for more details about filter policy.
        @return: self
            The self object for chaining purposes.
        '''
        return self.allFor(UPDATE, *services, filter=filter)
        
    def allDelete(self, *services, filter=None):
        '''
        Used for adding to the right the service calls that are Delete.
        
        @param service: arguments[service type]
            The services types to be used.
        @param filter: Filter|None
            The filter to be used with the added services, for more details about filter policy.
        @return: self
            The self object for chaining purposes.
        '''
        return self.allFor(DELETE, *services, filter=filter)
        
    def allModify(self, *services, filter=None):
        '''
        Used for adding to the right the service calls that modify the data (Insert, Update, Delete).
        
        @param service: arguments[service type]
            The services types to be used.
        @param filter: Filter|None
            The filter to be used with the added services, for more details about filter policy.
        @return: self
            The self object for chaining purposes.
        '''
        return self.allFor(INSERT | UPDATE | DELETE, *services, filter=filter)
        
    def all(self, *services, filter=None):
        '''
        Used for adding to the right all the service calls.
        
        @param service: arguments[service type]
            The services types to be used.
        @param filter: Filter|None
            The filter to be used with the added services, for more details about filter policy.
        @return: self
            The self object for chaining purposes.
        '''
        return self.allFor(GET | INSERT | UPDATE | DELETE, *services, filter=filter)

# --------------------------------------------------------------------

class Alternate:
    '''
    Provides the services alternates mappings.
    '''
    
    def __init__(self):
        '''
        Construct the alternates repository.
        '''
        self._alternates = {}
        
    def add(self, forRef, theRef):
        '''
        Adds 'theRef' reference as an alternate 'forRef' reference.
        
        @param forRef: tuple(class, string)
            The call reference for which the alternate is specified.
        @param theRef: tuple(class, string)
            The call reference which is an alternative the for reference.
        @return: self
            This instance for chaining purposes.
        '''
        assert isinstance(forRef, tuple), 'Invalid for reference %s' % forRef
        assert isinstance(theRef, tuple), 'Invalid the reference %s' % theRef
        clazz, forName = forRef
        forService = typeFor(clazz)
        assert isinstance(forService, TypeService), 'Invalid service class %s' % clazz
        assert isinstance(forService.service, Service)
        assert forName in forService.service.calls, 'Invalid service call name %s' % forName
        
        clazz, theName = theRef
        theService = typeFor(clazz)
        assert isinstance(theService, TypeService), 'Invalid service class %s' % clazz
        assert isinstance(theService.service, Service)
        assert theName in theService.service.calls, 'Invalid service call name %s' % theName
        
        key = (forService, forService.service.calls[forName])
        alternates = self._alternates.get(key)
        if alternates is None: alternates = self._alternates[key] = set()
        alternates.add((theService, theService.service.calls[theName]))
        
        return self
    
    def iterate(self):
        '''
        Iterates the alternates configured in this repository.
        
        @return: Iterable(tuple(TypeService, Call, Iterable(TypeService, Call)))
            The iterable containing the type service, call and the iterable of alternates also as type service and call.
        '''
        for serviceAndCall, alternates in self._alternates.items():
            yield serviceAndCall + (iter(alternates),)
      
# --------------------------------------------------------------------

class StructureRight:
    '''
    The structure root.
    '''
    
    def __init__(self):
        '''
        Construct the structure.
        
        @ivar methods: dictionary{integer, StructMethod)
            The method structure indexed by method.
        '''
        self.methods = {}

    def obtainMethod(self, call):
        '''
        Provides the structure method for the provided call.
        
        @param call: Call
            The call to provide the structure for.
        @return: StructMethod
            The structure method for the provided call.
        '''
        assert isinstance(call, Call), 'Invalid call %s' % call
        structMethod = self.methods.get(call.method)
        if not structMethod: structMethod = self.methods[call.method] = StructMethod()
        return structMethod
   
    def obtainCall(self, serviceType, call):
        '''
        Provides the structure call for the provided arguments.
        
        @param serviceType: TypeService
            The service type to provide the call structure for.
        @param call: Call
            The call to provide the structure for.
        @return: StructCall
            The call structure.
        '''
        return self.obtainMethod(call).obtainService(serviceType).obtainCall(serviceType, call)

class StructMethod:
    '''
    The structure for method.
    '''
    
    def __init__(self):
        '''
        Construct the method structure.
        
        @ivar services: dictionary{TypeService, StructService}
            The service structure indexed by service types.
        '''
        self.services = {}
        
    def obtainService(self, serviceType):
        '''
        Provides the structure method for the provided call.
        
        @param serviceType: TypeService
            The service type to provide the call structure for.
        @return: StructService
            The structure service for the provided service type.
        '''
        assert isinstance(serviceType, TypeService), 'Invalid service type %s' % serviceType
        structService = self.services.get(serviceType)
        if not structService: structService = self.services[serviceType] = StructService()
        return structService
    
class StructService:
    '''
    The structure for service.
    '''
    
    def __init__(self):
        '''
        Construct the service structure.
        
        @ivar calls: dictionary{string, StructCall}
            The call structure indexed by call name.
        '''
        self.calls = {}
        
    def obtainCall(self, serviceType, call):
        '''
        Provides the structure call for the provided arguments.
        
        @param serviceType: TypeService
            The service type to provide the call structure for.
        @param call: Call
            The call to provide the structure for.
        @return: StructCall
            The call structure.
        '''
        assert isinstance(call, Call), 'Invalid call %s' % call
        structCall = self.calls.get(call.name)
        if not structCall: structCall = self.calls[call.name] = StructCall(serviceType, call)
        return structCall
    
class StructCall:
    '''
    The cache for call.
    '''
    
    def __init__(self, serviceType, call):
        '''
        Construct the structure call for the provided service type and call.
        
        @param serviceType: TypeService
            The service type of the structure call.
        @param call: Call
            The call of the structure.
        @ivar filters: dictionary{TypeProperty: Filter}
            The Filter indexed by the filtered resource type for the call.
        '''
        assert isinstance(serviceType, TypeService), 'Invalid service type %s' % serviceType
        assert isinstance(call, Call), 'Invalid call %s' % call
        
        self.serviceType = serviceType
        self.call = call
        self.filters = {}

    def pushFilter(self, filter):
        '''
        Pushes the filter on this structure call. Read the filter policy of the right definition.
        
        @param filter: Filter
            The filter to push.
        '''
        assert isinstance(filter, Filter), 'Invalid filter %s' % filter
        filterOld = self.filters.get(filter.resource)
        if filterOld:
            assert isinstance(filterOld, Filter), 'Invalid filter %s' % filterOld
            if filter.priority > filterOld.priority: self.filters[filter.resource] = filter
        else: self.filters[filter.resource] = filter
