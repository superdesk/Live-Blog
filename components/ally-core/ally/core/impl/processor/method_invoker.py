'''
Created on Jul 14, 2011

@package: Newscoop
@copyright: 2011 Sourcefabric o.p.s.
@license: http://www.gnu.org/licenses/gpl-3.0.txt
@author: Gabriel Nistor

Provides the requested method validation handler.
'''

from ally.api.config import GET, INSERT, UPDATE, DELETE
from ally.api.type import Type
from ally.core.spec.codes import METHOD_NOT_AVAILABLE, Code
from ally.core.spec.resources import Path, Node, Invoker
from ally.design.context import Context, requires, defines
from ally.design.processor import Chain, HandlerProcessor

# --------------------------------------------------------------------

class Request(Context):
    '''
    The request context.
    '''
    # ---------------------------------------------------------------- Required
    method = requires(int)
    path = requires(Path)
    # ---------------------------------------------------------------- Defined
    invoker = defines(Invoker, doc='''
    @rtype: Invoker
    The invoker to be used for calling the service.
    ''')

class Response(Context):
    '''
    The response context.
    '''
    # ---------------------------------------------------------------- Defined
    code = defines(Code)
    text = defines(str)
    allows = defines(int, doc='''
    @rtype: integer
    Contains the allow flags for the methods.
    ''')
    metaForType = defines(Type, doc='''
    @rtype: Type
    The type to construct the meta for.
    ''')

# --------------------------------------------------------------------

class MethodInvokerHandler(HandlerProcessor):
    '''
    Implementation for a processor that validates if the request method (GET, INSERT, UPDATE, DELETE) is compatible
    with the resource node of the request, basically checks if the node has the invoke for the requested method.
    If the node has no invoke than this processor will stop the execution chain and provide an error response also
    providing the allows methods for the resource path node.
    '''

    def __init__(self):
        super().__init__()

    def process(self, chain, request:Request, response:Response, **keyargs):
        '''
        @see: HandlerProcessor.process
        
        Provide the invoker based on the request method to be used in getting the data for the response.
        '''
        assert isinstance(chain, Chain), 'Invalid processors chain %s' % chain
        assert isinstance(request, Request), 'Invalid request %s' % request
        assert isinstance(response, Response), 'Invalid response %s' % response
        assert isinstance(request.path, Path), 'Invalid request path %s' % request.path
        node = request.path.node
        assert isinstance(node, Node), 'Invalid request path node %s' % node

        if request.method == GET: # Retrieving
            request.invoker = node.get
            if request.invoker is None:
                response.code, response.text = METHOD_NOT_AVAILABLE, 'Path not available for GET'
                response.allows = self.allowedFor(node)
                return
        elif request.method == INSERT: # Inserting
            request.invoker = node.insert
            if request.invoker is None:
                response.code, response.text = METHOD_NOT_AVAILABLE, 'Path not available for POST'
                response.allows = self.allowedFor(node)
                return
        elif request.method == UPDATE: # Updating
            request.invoker = node.update
            if request.invoker is None:
                response.code, response.text = METHOD_NOT_AVAILABLE, 'Path not available for PUT'
                response.allows = self.allowedFor(node)
                return
        elif request.method == DELETE: # Deleting
            request.invoker = node.delete
            if request.invoker is None:
                response.code, response.text = METHOD_NOT_AVAILABLE, 'Path not available for DELETE'
                response.allows = self.allowedFor(node)
                return
        else:
            response.code, response.text = METHOD_NOT_AVAILABLE, 'Path not available for method'
            response.allows = self.allowedFor(node)
            return

        response.metaForType = request.invoker.output

        chain.proceed()

    # ----------------------------------------------------------------

    def allowedFor(self, node):
        '''
        Get the allow flags for the provided node.
        
        @param node: Node
            The node to get the allow flags.
        @return: integer
            The allow falgs.
        '''
        assert isinstance(node, Node), 'Invalid node %s' % node

        allows = 0
        if node.get is not None: allows |= GET
        if node.insert is not None: allows |= INSERT
        if node.update is not None: allows |= UPDATE
        if node.delete is not None: allows |= DELETE

        return allows
