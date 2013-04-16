'''
Created on Jan 19, 2013

@package: support acl
@copyright: 2012 Sourcefabric o.p.s.
@license: http://www.gnu.org/licenses/gpl-3.0.txt
@author: Gabriel Nistor

Provides the ACL specifications.
'''

from ally.api.operator.type import TypeProperty
from ally.api.type import typeFor
from collections import Iterable

# --------------------------------------------------------------------

class Filter:
    '''
    The filter model contains data describes a filter to be used for a certain call or calls.
    '''
    
    def __init__(self, priority, authenticated, resource, filter):
        '''
        Construct the acl filter.
        
        @param priority: integer
            The priority of the filter, this is used whenever there are more then one filter in the same context in order to
            establish which one will be used. A higher value means a higher priority.
        @param authenticated: TypeProperty
            The property type of the authenticated resource specific for the action taker.
        @param resource: TypeProperty
            The property type that is targeted for filtering.
        @param filter: object
            The filter is an object that can be used by the security services in order to filter the authenticated vs resource.
        '''
        assert isinstance(priority, int), 'Invalid priority %s' % priority
        authenticated = typeFor(authenticated)
        assert isinstance(authenticated, TypeProperty), 'Invalid property type %s' % authenticated
        resource = typeFor(resource)
        assert isinstance(resource, TypeProperty), 'Invalid property type %s' % resource
        
        self.priority = priority
        self.authenticated = authenticated
        self.resource = resource
        self.filter = filter

class RightAcl:
    '''
    The ACL right model base
    '''
    
    def __init__(self, name, description):
        '''
        Construct the right model.
        
        @param name: string
            The right name.
        @param description: string
            The description for the right.
        '''
        assert isinstance(name, str), 'Invalid name %s' % name
        assert isinstance(description, str), 'Invalid description %s' % description
        
        self.name = name.strip()
        self.description = description.strip()
        self.type = None

class TypeAcl:
    '''
    The ACL type model.
    '''
    
    def __init__(self, name, description):
        '''
        Construct the type model.
        
        @param name: string
            The type name.
        @param description: string
            The description for the type.
        '''
        assert isinstance(name, str), 'Invalid name %s' % name
        assert isinstance(description, str), 'Invalid description %s' % description
        self.name = name.strip()
        self.description = description.strip()
        self._rights = {}
        self._defaults = []
            
    rights = property(lambda self: self._rights.values(), doc=
'''
@type rights: Iterable(RightAcl)
    The rights for the type.
''')
    defaults = property(lambda self: iter(self._defaults), doc=
'''
@type defaults: Iterable(RightAcl)
    The default rights for the type.
''')
    
    def rightsFor(self, names):
        '''
        Provides the rights for the provided name(s).
        
        @param names: string|Iterable(string)
            The name(s) to provide rights for.
        @return: Iterable(RightAcl)
            The rights that correspond with the provided names.
        '''
        if isinstance(names, str): names = (names,)
        assert isinstance(names, Iterable), 'Invalid names %s' % names
        for name in names:
            assert isinstance(name, str), 'Invalid name %s' % name
            right = self._rights.get(name)
            if right: yield right
    
    def add(self, right):
        '''
        Add a new ACL right that is binded to this ACL type.
        
        @param right: RightAcl
            The ACL right to be added.
        @return: RightAcl
            The same right.
        '''
        assert isinstance(right, RightAcl), 'Invalid right %s' % right
        assert right.name not in self._rights, 'Already a right with name %s' % right.name
        assert right.type is None, 'The right %s already has a type' % right.type
        self._rights[right.name] = right
        right.type = self
        return right
    
    def addDefault(self, right):
        '''
        Add a default ACL right that is binded to this ACL type. The default rights are always present when there is a single
        right for that type.
        
        @param right: RightAcl
            The ACL right to be added.
        @return: RightAcl
            The same right.
        '''
        assert isinstance(right, RightAcl), 'Invalid right %s' % right
        assert right.type is None, 'The right %s already has a type' % right.type
        self._defaults.append(right)
        right.type = self
        return right
    
class Acl:
    '''
    The ACL repository.
    '''
    
    def __init__(self):
        '''
        Construct the ACL repository.
        '''
        self._types = {}
        
    types = property(lambda self: self._types.values(), doc=
'''
@type types: Iterable(TypeAcl)
    The types for the acl repository.
''')
        
    def add(self, type):
        '''
        Add a new ACL type that is binded to this ACL repository.
        
        @param type: TypeAcl
            The ACL type to be added.
        @return: Type
            The same type.
        '''
        assert isinstance(type, TypeAcl), 'Invalid type %s' % type
        assert type.name not in self._types, 'Already a type with name %s' % type.name
        self._types[type.name] = type
        return type
