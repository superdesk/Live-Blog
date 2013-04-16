'''
Created on Jul 14, 2011

@package: ally core http
@copyright: 2011 Sourcefabric o.p.s.
@license: http://www.gnu.org/licenses/gpl-3.0.txt
@author: Gabriel Nistor

Provides the requested method validation handler.
'''

from ally.core.spec.resources import Path, Node, Invoker
from ally.design.processor.attribute import requires, defines
from ally.design.processor.context import Context
from ally.design.processor.handler import HandlerProcessorProceed
from ally.http.spec.codes import METHOD_NOT_AVAILABLE
from ally.http.spec.server import HTTP_GET, HTTP_POST, HTTP_PUT, HTTP_DELETE

# --------------------------------------------------------------------

class Request(Context):
    method = requires(str)
    path = requires(Path)
    invoker = defines(Invoker)

class Response(Context):
    code = defines(str)
    status = defines(int)
    isSuccess = defines(bool)
    allows = defines(list)

# --------------------------------------------------------------------

class MethodInvokerHandler(HandlerProcessorProceed):
    '''
    Implementation for a processor that validates if the request method (GET, POST, PUT, DELETE) is compatible
    with the resource node of the request, basically checks if the node has the invoke for the requested method.
    If the node has no invoke than this processor will provide an error response for the resource path node.
    '''

    def process(self, request:Request, response:Response, **keyargs):
        '''
        @see: HandlerProcessorProceed.process
        
        Provide the invoker based on the request method to be used in getting the data for the response.
        '''
        assert isinstance(request, Request), 'Invalid request %s' % request
        assert isinstance(response, Response), 'Invalid response %s' % response
        if response.isSuccess is False: return  # Skip in case the response is in error

        assert isinstance(request.path, Path), 'Invalid request path %s' % request.path
        node = request.path.node
        assert isinstance(node, Node), 'Invalid request path node %s' % node

        if request.method == HTTP_GET: request.invoker = node.get  # Retrieving
        elif request.method == HTTP_POST: request.invoker = node.insert  # Inserting
        elif request.method == HTTP_PUT: request.invoker = node.update  # Updating
        elif request.method == HTTP_DELETE: request.invoker = node.delete  # Deleting

        if request.invoker is None:
            response.code, response.status, response.isSuccess = METHOD_NOT_AVAILABLE
            if response.allows is None: response.allows = []
            
            if node.get is not None: response.allows.append(HTTP_GET)
            if node.insert is not None: response.allows.append(HTTP_POST)
            if node.update is not None: response.allows.append(HTTP_PUT)
            if node.delete is not None: response.allows.append(HTTP_DELETE)
