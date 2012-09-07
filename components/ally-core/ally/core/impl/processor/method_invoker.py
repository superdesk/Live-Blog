'''
Created on Jul 14, 2011

@package: ally core
@copyright: 2011 Sourcefabric o.p.s.
@license: http://www.gnu.org/licenses/gpl-3.0.txt
@author: Gabriel Nistor

Provides the requested method validation handler.
'''

from ally.api.config import GET, INSERT, UPDATE, DELETE
from ally.container.ioc import injected
from ally.core.spec.codes import METHOD_NOT_AVAILABLE
from ally.core.spec.resources import Path, Node
from ally.core.spec.server import Processor, Request, Response, ProcessorsChain

# --------------------------------------------------------------------

@injected
class MethodInvokerHandler(Processor):
    '''
    Implementation of a processor that validates if the request method (GET, INSERT, UPDATE, DELETE) is compatible
    with the resource node of the request, basically checks if the node has the invoke for the requested method.
    If the node has no invoke than this processor will stop the execution chain and provide an error response also
    providing the allowed methods for the resource path node.
    
    Provides on request: invoker, objType
    Provides on response: NA
    
    Requires on request: method, resourcePath
    Requires on response: NA
    '''

    def process(self, req, rsp, chain):
        '''
        @see: Processor.process
        '''
        assert isinstance(req, Request), 'Invalid request %s' % req
        assert isinstance(rsp, Response), 'Invalid response %s' % rsp
        assert isinstance(chain, ProcessorsChain), 'Invalid processors chain %s' % chain
        path = req.resourcePath
        assert isinstance(path, Path)
        node = path.node
        assert isinstance(node, Node), \
        'The node has to be available in the path %s problems in previous processors' % path
        if req.method == GET: # Retrieving
            req.invoker = node.get
            if req.invoker is None:
                self._sendNotAvailable(node, rsp, 'Path not available for get')
                return
        elif req.method == INSERT: # Inserting
            req.invoker = node.insert
            if req.invoker is None:
                self._sendNotAvailable(node, rsp, 'Path not available for post')
                return
        elif req.method == UPDATE: # Updating
            req.invoker = node.update
            if req.invoker is None:
                self._sendNotAvailable(node, rsp, 'Path not available for put')
                return
        elif req.method == DELETE: # Deleting
            req.invoker = node.delete
            if req.invoker is None:
                self._sendNotAvailable(node, rsp, 'Path not available for delete')
                return
        else:
            self._sendNotAvailable(node, rsp, 'Path not available for this method')
            return
        rsp.objType = req.invoker.output
        chain.proceed()

    def _processAllow(self, node, rsp):
        '''
        Set the allows for the response based on the provided node.
        '''
        assert isinstance(node, Node)
        assert isinstance(rsp, Response)
        if node.get is not None:
            rsp.addAllows(GET)
        if node.insert is not None:
            rsp.addAllows(INSERT)
        if node.update is not None:
            rsp.addAllows(UPDATE)
        if node.delete is not None:
            rsp.addAllows(DELETE)

    def _sendNotAvailable(self, node, rsp, message):
        self._processAllow(node, rsp)
        rsp.setCode(METHOD_NOT_AVAILABLE, message)
