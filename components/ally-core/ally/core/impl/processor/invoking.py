'''
Created on Jun 30, 2011

@package: Newscoop
@copyright: 2011 Sourcefabric o.p.s.
@license: http://www.gnu.org/licenses/gpl-3.0.txt
@author: Gabriel Nistor

Provides the invoking handler.
'''

from ally.api.operator import GET, INSERT, UPDATE, DELETE
from ally.container.ioc import injected
from ally.core.spec.codes import INTERNAL_ERROR, RESOURCE_NOT_FOUND, \
    DELETED_SUCCESS, CANNOT_DELETE, UPDATE_SUCCESS, CANNOT_UPDATE, INSERT_SUCCESS, \
    CANNOT_INSERT, BAD_CONTENT
from ally.core.spec.resources import Path, Invoker, ResourcesManager
from ally.core.spec.server import Processor, ProcessorsChain, Response, Request
from ally.exception import DevelException, InputException
from ally.support.api.util_type import isPropertyTypeId
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
    
    Provides on request: NA
    Provides on response: obj, objType
    
    Requires on request: invoker, resourcePath
    Requires on response: NA
    '''
    
    resourcesManager = ResourcesManager
    # The resources manager used in locating the resource paths for the id's presented.
    
    def __init__(self):
        assert isinstance(self.resourcesManager, ResourcesManager), \
        'Invalid resources manager %s' % self.resourcesManager
        self._callback = {GET: self._afterGet, INSERT: self._afterInsert,
                          UPDATE: self._afterUpdate, DELETE: self._afterDelete}
    
    def process(self, req, rsp, chain):
        '''
        @see: Processor.process
        '''
        assert isinstance(chain, ProcessorsChain), 'Invalid processors chain %s' % chain
        assert isinstance(req, Request), 'Invalid request %s' % req
        assert isinstance(rsp, Response), 'Invalid response %s' % rsp
        path = req.resourcePath
        assert isinstance(path, Path)
        callback = self._callback.get(req.method)
        if not callback: raise AssertionError('Cannot process request method %s' % req.method)
        
        arguments = {}
        invoke = [req.invoker, arguments, rsp, callback]
        
        if req.method == DELETE:
            arguments.update(path.toArguments(req.invoker))
        else:
            arguments.update(path.toArguments(req.invoker))
            arguments.update(req.arguments)
            if req.method == INSERT: invoke.append(path)
            
        if self._invoke(*invoke): chain.process(req, rsp)
    
    # ----------------------------------------------------------------
    
    def _afterGet(self, value, invoker, rsp):
        '''
        Process the after get action on the value.
        
        @param value: object
        @param invoker: Invoker
        @param rsp: Response
        
        @return: boolean
            False if the invoking has failed, True for success.
        '''
        assert isinstance(rsp, Response)
        assert isinstance(invoker, Invoker)
        rsp.objType = invoker.outputType
        rsp.obj = value
        return True
    
    def _afterInsert(self, value, invoker, rsp, path):
        '''
        Process the after insert action on the value.
        
        @param value: object
        @param invoker: Invoker
        @param rsp: Response
        @param path: Path
        
        @return: boolean
            False if the invoking has failed, True for success.
        '''
        assert isinstance(rsp, Response)
        assert isinstance(invoker, Invoker)
        if isPropertyTypeId(invoker.outputType):
            if value is not None:
                path = self.resourcesManager.findGetModel(path, invoker.outputType.model)
                if path:
                    path.update(value, invoker.outputType)
                    rsp.contentLocation = path
                else:
                    rsp.objType = invoker.outputType
                    rsp.obj = value
            else:
                rsp.setCode(CANNOT_INSERT, 'Cannot insert')
                assert log.debug('Cannot updated resource') or True
                return False
        else:
            rsp.objType = invoker.outputType
            rsp.obj = value
        rsp.setCode(INSERT_SUCCESS, 'Successfully created')
        return True
    
    def _afterUpdate(self, value, invoker, rsp):
        '''
        Process the after update action on the value.
        
        @param value: object
        @param invoker: Invoker
        @param rsp: Response
        
        @return: boolean
            False if the invoking has failed, True for success.
        '''
        assert isinstance(rsp, Response)
        assert isinstance(invoker, Invoker)
        if invoker.outputType.isOf(None):
            rsp.setCode(UPDATE_SUCCESS, 'Successfully updated')
            assert log.debug('Successful updated resource') or True
        elif invoker.outputType.isOf(bool):
            if value == True:
                rsp.setCode(UPDATE_SUCCESS, 'Successfully updated')
                assert log.debug('Successful updated resource') or True
            else:
                rsp.setCode(CANNOT_UPDATE, 'Cannot updated')
                assert log.debug('Cannot updated resource') or True
            return False
        else:
            #If an entity is returned than we will render that.
            rsp.objType = invoker.outputType
            rsp.obj = value
        return True
    
    def _afterDelete(self, value, invoker, rsp):
        '''
        Process the after delete action on the value.
        
        @param value: object
        @param invoker: Invoker
        @param rsp: Response
        
        @return: boolean
            False if the invoking has failed, True for success.
        '''
        assert isinstance(rsp, Response)
        assert isinstance(invoker, Invoker)
        if invoker.outputType.isOf(bool):
            if value == True:
                rsp.setCode(DELETED_SUCCESS, 'Successfully deleted')
                assert log.debug('Successful deleted resource') or True
            else:
                rsp.setCode(CANNOT_DELETE, 'Cannot delete')
                assert log.debug('Cannot deleted resource') or True
            return False
        else:
            #If an entity is returned than we will render that.
            rsp.objType = invoker.outputType
            rsp.obj = value
        return True
    
    def _invoke(self, invoker, arguments, rsp, callback, *args):
        '''
        Process the invoking.
        
        @param invoker: Invoker
        @param arguments: dictionary{string, object}
        @param rsp: Response
        @param callback: Callable(object, Invoker, Response)
        
        @return: boolean
            False if the invoking has failed, True for success.
        '''
        assert isinstance(invoker, Invoker)
        assert isinstance(rsp, Response)
        try:
            value = invoker.invoke(*[arguments[inp.name] if inp.name in arguments else None
                                     for inp in invoker.inputs ])
            assert log.debug('Successful on calling invoker %s with values %s', invoker, args) or True
            return callback(value, invoker, rsp, *args)
        except DevelException as e:
            rsp.setCode(BAD_CONTENT, e.message)
            log.info('Problems with the invoked content: %s', e.message, exc_info=True)
        except InputException as e:
            rsp.setCode(RESOURCE_NOT_FOUND, e, 'Invalid resource')
            assert log.debug('User input exception: %s', e, exc_info=True) or True
        except:
            rsp.setCode(INTERNAL_ERROR, 'Upps, it seems I am in a pickle, please consult the server logs')
            log.exception('An exception occurred while trying to invoke %s with values %s', invoker, args)
        return False
