'''
Created on Jun 30, 2011

@package: Newscoop
@copyright: 2011 Sourcefabric o.p.s.
@license: http://www.gnu.org/licenses/gpl-3.0.txt
@author: Gabriel Nistor

Provides the invoking handler.
'''

from ally.api.config import GET, INSERT, UPDATE, DELETE
from ally.container.ioc import injected
from ally.core.spec.codes import INTERNAL_ERROR, RESOURCE_NOT_FOUND, \
    DELETED_SUCCESS, CANNOT_DELETE, UPDATE_SUCCESS, CANNOT_UPDATE, INSERT_SUCCESS, \
    CANNOT_INSERT, BAD_CONTENT
from ally.core.spec.resources import Path, Invoker
from ally.core.spec.server import Processor, ProcessorsChain, Response, Request
from ally.exception import DevelError, InputError
import logging
from ally.api.operator.type import TypeModelProperty

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
    Provides on response: obj
    
    Requires on request: invoker, resourcePath
    Requires on response: NA
    '''

    def __init__(self):
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

        if self._invoke(*invoke): chain.proceed()

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
        if isinstance(invoker.output, TypeModelProperty) and \
        invoker.output.container.propertyId == invoker.output.property:
            if value is not None:
                rsp.obj = value
            else:
                rsp.setCode(CANNOT_INSERT, 'Cannot insert')
                assert log.debug('Cannot updated resource') or True
                return False
        else:
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
        if invoker.output.isOf(None):
            rsp.setCode(UPDATE_SUCCESS, 'Successfully updated')
            assert log.debug('Successful updated resource') or True
        elif invoker.output.isOf(bool):
            if value == True:
                rsp.setCode(UPDATE_SUCCESS, 'Successfully updated')
                assert log.debug('Successful updated resource') or True
            else:
                rsp.setCode(CANNOT_UPDATE, 'Cannot updated')
                assert log.debug('Cannot updated resource') or True
            return False
        else:
            #If an entity is returned than we will render that.
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
        if invoker.output.isOf(bool):
            if value == True:
                rsp.setCode(DELETED_SUCCESS, 'Successfully deleted')
                assert log.debug('Successful deleted resource') or True
            else:
                rsp.setCode(CANNOT_DELETE, 'Cannot delete')
                assert log.debug('Cannot deleted resource') or True
            return False
        else:
            #If an entity is returned than we will render that.
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
        assert isinstance(invoker, Invoker), 'Invalid invoker %s' % invoker
        assert isinstance(rsp, Response), 'Invalid response %s' % rsp
        try:
            value = invoker.invoke(*(arguments[inp.name] if inp.name in arguments else inp.default
                                     for inp in invoker.inputs))
            assert log.debug('Successful on calling invoker %s with values %s', invoker, args) or True
            return callback(value, invoker, rsp, *args)
        except DevelError as e:
            rsp.setCode(BAD_CONTENT, e.message)
            log.info('Problems with the invoked content: %s', e.message, exc_info=True)
        except InputError as e:
            rsp.setCode(RESOURCE_NOT_FOUND, e, 'Invalid resource')
            assert log.debug('User input exception: %s', e, exc_info=True) or True
        except:
            rsp.setCode(INTERNAL_ERROR, 'Upps, it seems I am in a pickle, please consult the server logs')
            log.exception('An exception occurred while trying to invoke %s with values %s', invoker, args)
        return False
