'''
Created on Jan 23, 2012

@package: introspection request
@copyright: 2011 Sourcefabric o.p.s.
@license: http://www.gnu.org/licenses/gpl-3.0.txt
@author: Nistor Gabriel

API specifications for the node presenter.
'''

from admin.api.domain_admin import modelAdmin
from ally.api.config import service, call
from ally.api.type import Iter

# --------------------------------------------------------------------

@modelAdmin(id='Id')
class MethodPrototype:
    '''
    Provides a call method of a request.
    '''
    Id = int
    Name = str
    Type = str
    APIClass = str
    APIClassDefiner = str
    APIDoc = str
    IMPL = str
    IMPLDefiner = str
    IMPLDoc = str

@modelAdmin(id='Id')
class Request:
    '''
    Provides the request.
    '''
    Id = int
    Pattern = str
    Get = MethodPrototype
    Delete = MethodPrototype
    Insert = MethodPrototype
    Update = MethodPrototype

@modelAdmin(replace=MethodPrototype)
class Method(MethodPrototype):
    '''
    Provides a call method of a request.
    '''
    ForRequest = Request

@modelAdmin(id='Id')
class Input:
    '''
    Provides the input.
    '''
    Id = int
    ForRequest = Request
    Name = str
    Mandatory = bool
    Description = str

# --------------------------------------------------------------------

@service
class IRequestService:
    '''
    Provides services for the request nodes.
    '''

    @call
    def getRequest(self, id:Request.Id) -> Request:
        '''
        Provides the request for the provided id.
        '''

    @call
    def getMethod(self, id:Method.Id) -> Method:
        '''
        Provides the method for the provided id.
        '''

    @call
    def getAllInputs(self, id:Request.Id=None) -> Iter(Input):
        '''
        Provides all the pattern inputs.
        '''

    @call
    def getAllRequests(self, offset:int=None, limit:int=None) -> Iter(Request):
        '''
        Provides all the request nodes.
        '''
