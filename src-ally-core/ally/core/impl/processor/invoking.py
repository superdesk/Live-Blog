'''
Created on Jun 30, 2011

@package: Newscoop
@copyright: 2011 Sourcefabric o.p.s.
@license: http://www.gnu.org/licenses/gpl-3.0.txt
@author: Gabriel Nistor

Provides the invoking handler.
'''

from ally.api.operator import GET, INSERT, UPDATE, DELETE
from ally.core.impl.util_type import isPropertyTypeId
from ally.core.spec.codes import INTERNAL_ERROR, RESOURCE_NOT_FOUND, \
    DELETED_SUCCESS, CANNOT_DELETE, UPDATE_SUCCESS, CANNOT_UPDATE, INSERT_SUCCESS, \
    CANNOT_INSERT, BAD_CONTENT
from ally.exception import DevelException, InputException
from ally.core.spec.resources import Path, Node, Invoker, ResourcesManager
from ally.core.spec.server import Processor, ProcessorsChain, Response, Request
from ally.ioc import injected
import logging

# --------------------------------------------------------------------

log = logging.getLogger(__name__)

# --------------------------------------------------------------------

@injected
class InvokingHandler(Processor):
    '''
    Implementation for a processor that makes the actual call to the request method corresponding invoke on the
    resource path node. The invoking will use all the obtained arguments from the previous processors and perform
    specific actions based on the requested method. In GET case it will provide to the request the invoke returned
    object as to be rendered to the response, in DELETE case it will stop the execution chain and send as a response
    a success code.
    '''
    
    resourcesManager = ResourcesManager
    # The resources manager used in locating the resource paths for the id's presented.
    
    def __init__(self):
        assert isinstance(self.resourcesManager, ResourcesManager), \
        'Invalid resources manager %s' % self.resourcesManager
    
    def process(self, req, rsp, chain):
        '''
        @see: Processor.process
        '''
        assert isinstance(chain, ProcessorsChain), 'Invalid processors chain %s' % chain
        assert isinstance(req, Request), 'Invalid request %s' % req
        assert isinstance(rsp, Response), 'Invalid response %s' % rsp
        path = req.resourcePath
        assert isinstance(path, Path)
        node = path.node
        assert isinstance(node, Node)
        assert isinstance(req.invoker, Invoker)
        if req.method == GET: # Retrieving
            argsDict = path.toArguments(req.invoker)
            argsDict.update(req.arguments)
            try:
                rsp.objType = req.invoker.outputType
                rsp.obj = self._invoke(req.invoker, argsDict, rsp)
            except: return
        elif req.method == INSERT: # Inserting
            argsDict = path.toArguments(req.invoker)
            argsDict.update(req.arguments)
            try:
                value = self._invoke(req.invoker, argsDict, rsp)
            except: return
            if isPropertyTypeId(req.invoker.outputType):
                if value is not None:
                    path = self.resourcesManager.findGetModel(req.resourcePath, req.invoker.outputType.model)
                    if path:
                        path.update(value, req.invoker.outputType)
                        rsp.contentLocation = path
                    else:
                        rsp.objType = req.invoker.outputType
                        rsp.obj = value
                else:
                    rsp.setCode(CANNOT_INSERT, 'Cannot insert')
                    assert log.debug('Cannot updated resource') or True
                    return
            else:
                rsp.objType = req.invoker.outputType
                rsp.obj = value
            rsp.setCode(INSERT_SUCCESS, 'Successfully created')
        elif req.method == UPDATE: # Updating
            argsDict = path.toArguments(req.invoker)
            argsDict.update(req.arguments)
            try:
                value = self._invoke(req.invoker, argsDict, rsp)
            except: return
            if req.invoker.outputType.isOf(None):
                rsp.setCode(UPDATE_SUCCESS, 'Successfully updated')
                assert log.debug('Successful updated resource') or True
            elif req.invoker.outputType.isOf(bool):
                if value == True:
                    rsp.setCode(UPDATE_SUCCESS, 'Successfully updated')
                    assert log.debug('Successful updated resource') or True
                else:
                    rsp.setCode(CANNOT_UPDATE, 'Cannot updated')
                    assert log.debug('Cannot updated resource') or True
                return
            else:
                #If an entity is returned than we will render that.
                rsp.objType = req.invoker.outputType
                rsp.obj = value
        elif req.method == DELETE: # Deleting
            try:
                value = self._invoke(req.invoker, path.toArguments(req.invoker), rsp)
            except: return
            if req.invoker.outputType.isOf(bool):
                if value == True:
                    rsp.setCode(DELETED_SUCCESS, 'Successfully deleted')
                    assert log.debug('Successful deleted resource') or True
                else:
                    rsp.setCode(CANNOT_DELETE, 'Cannot delete')
                    assert log.debug('Cannot deleted resource') or True
                return
            else:
                #If an entity is returned than we will render that.
                rsp.objType = req.invoker.outputType
                rsp.obj = value
        else:
            raise AssertionError('Cannot process request method %s' % req.method)
        chain.process(req, rsp)
        
    def _invoke(self, invoker, argsDict, rsp):
        args = []
        for inp in invoker.inputs:
            try:
                args.append(argsDict[inp.name])
            except KeyError:
                args.append(None)
        try:
            value = invoker.invoke(*args)
            assert log.debug('Successful on calling invoker %s with values %s', invoker, args) or True
            return value
        except DevelException as e:
            rsp.setCode(BAD_CONTENT, e.message)
            log.warning('Problems with the invoked content: %s', e.message)
            raise
        except InputException as e:
            rsp.setCode(RESOURCE_NOT_FOUND, e, 'Invalid resource')
            assert log.exception('User input exception: %s', e) or True
            raise
        except:
            rsp.setCode(INTERNAL_ERROR, 'Upps, it seems I am in a pickle, please consult the server logs')
            log.exception('An exception occurred while trying to invoke %s with values %s', \
                      invoker, args)
            raise
